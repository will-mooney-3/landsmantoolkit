"""Main file for the application.
@author Will Mooney (will.mooney.3@gmail.com)
"""

import fnmatch
import os
import sys

# As in PIL's Image object...
import Image
import tesseract


class Application(object):
    """This really needs to be broken up better, but I'm throwing this together
    pretty quickly.
    """

    COMPLETED_TEXT_EXTRACTION = "Completed text extraction. {0} files are less than {1}% confidence"
    OCR_CONFIDENCE_THRESHOLD = 70
    TEXT_FILE_PREFIX = ""
    TEXT_FILE_SUFFIX = ""
    TEXT_FILE_EXTENSION = ".txt"

    def __init__(self):
        """"""
        super(Application, self).__init__()
        self.file_roots_and_names = []
        self.potential_problem_files = []
        self.searchable_files = []
        self.tesseract_api = tesseract.TessBaseAPI()
        self.tesseract_api.Init(".", "eng", tesseract.OEM_DEFAULT)
        self.tesseract_api.SetPageSegMode(tesseract.PSM_AUTO)

    def display_menu(self):
        """Display the main menu for the program and return the selected option.
        @return The int option selected
        """
        print ""
        print ""
        print ""
        print "==============================================================="
        print "Will's Text Extraction and Search Program!"
        print "==============================================================="
        print "1. Perform text extraction on all TIF files in this folder and subfolders"
        print "2. Search previously extracted text for a case insensitive name or term"
        print "3. Same as 2, but case sensitive"
        print "4. Exit"
        print ""
        print "Enter the number of the option you would like to select"
        print ""
        selection = raw_input("My selection: ")
        try:
            selection = int(selection)
        except Exception:
            print "I'll give you another chance at that..."
            selection = self.display_menu()
        return selection

    def get_all_matching_files(self, file_list, file_extension="tif",
                               working_directory=None):
        """Get all of the files in the current folder and below.
        @param file_extension str File Extension to look for
        """
        if not working_directory:
            working_directory = os.getcwd()
        ext_pattern = "*.{0}".format(file_extension)
        for root, dirnames, filenames in os.walk(working_directory):
            for filename in fnmatch.filter(filenames, ext_pattern):
                file_list.append((root, filename))

    def pull_text_from_file(self, root, filename):
        """Use OCR to extract the text from the file. Writes the text to file
        @param root The str root of the file path
        @param filename The name of the file to pull from
        """
        full_path = os.path.join(root, filename)
        text_file_path = "{0}{1}{2}{3}".format(self.TEXT_FILE_PREFIX,
                                               filename,
                                               self.TEXT_FILE_SUFFIX,
                                               self.TEXT_FILE_EXTENSION)
        text_file_path = os.path.join(root, text_file_path)
        if not os.path.isfile(text_file_path):
            with open(full_path, "rb") as buffer:
                buffer = buffer.read()
                text_pulled = tesseract.ProcessPagesBuffer(buffer, len(buffer),
                                                           self.tesseract_api)
                if self.tesseract_api.MeanTextConf() >= self.OCR_CONFIDENCE_THRESHOLD:
                    with open(text_file_path, "w") as text_file:
                        text_file.write(text_pulled)
                else:
                    self.potential_problem_files.append(root, filename)

    def run_text_extraction(self, extention="tif", working_directory=None):
        """Performs text extraction. No user input needed, outputs completion
        percentage as it goes and a message when complete.
        """
        if not self.file_roots_and_names:
            self.get_all_matching_files(self.file_roots_and_names,
                                        file_extension=extention,
                                        working_directory=working_directory)
        number_of_files = len(self.file_roots_and_names)
        files_completed = 0
        percentage_complete = 0.0
        for root, filename in self.file_roots_and_names:
            self.pull_text_from_file(root, filename)
            files_completed += 1
            percentage_complete = float(files_completed) / float(number_of_files)
            percentage_complete *= 100
            sys.stdout.write("\rText extraction: %.2f%% complete" % percentage_complete)
            sys.stdout.flush()
        print ""
        print self.COMPLETED_TEXT_EXTRACTION.format(len(self.potential_problem_files),
                                                    self.OCR_CONFIDENCE_THRESHOLD)
        for root, filename in self.potential_problem_files:
            print os.path.join(root, filename)

    def run(self):
        """Show the menu and preform the selected action."""
        while True:
            option = self.display_menu()
            if option == 4:
                sys.exit(0)
            elif option == 1:
                self.run_text_extraction(working_directory=None)
            elif option == 2:
                self.search_extracted_text()
            elif option == 3:
                self.search_extracted_text(case_insensitive=False)

    def search_extracted_text(self, case_insensitive=True):
        """Search all of the extracted text files for a given term. Gets user
        input for the term, outputs the 
        """
        if not self.searchable_files:
            self.get_all_matching_files(self.searchable_files,
                                        file_extension="txt")
        if len(self.searchable_files) < 1:
            print "I can't seem to find any text files to search..."
            print "Make sure you ran option 1 from the main menu to generate them."
            return
        print ""
        print "Found {0} files to search.".format(len(self.searchable_files))
        search_term = raw_input("What would you like to search for? ")
        print ""
        if case_insensitive:
            search_term = search_term.lower()
        print "Now searching {0} files for {1}".format(len(self.searchable_files),
                                                       search_term)
        some_results = False
        for root, filename in self.searchable_files:
            results = self.search_file_for_term(root, filename, search_term,
                                                case_insensitive=case_insensitive)
            if results:
                some_results = True
                number_of_matches = len(results)
                print ""
                print ""
                print "{0} has {1} matches...".format(os.path.join(root, filename), number_of_matches)
                print ""
                for result in results:
                    print "[LINE {0}] {1}".format(result[0], result[1])
        if not some_results:
            print "No matches for {0}. Sorry! :(".format(search_term)

    def search_file_for_term(self, root, filename, term, case_insensitive=True):
        """Search through the given file for the given term.
        @param root The root of the file's location
        @param filename The name of the file to search
        @param term The str term to search for
        @return list of tuples (line number, line that matched)
        """
        results = []
        with open(os.path.join(root, filename), "r") as search_file:
            line_number = 0
            for line in search_file:
                search_line = line
                if case_insensitive:
                    search_line = search_line.lower()
                line_number += 1
                if term in search_line:
                    results.append((line_number, line))
        return results


if __name__ == '__main__':
    Application().run()
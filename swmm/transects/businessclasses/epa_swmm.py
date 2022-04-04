from enum import Enum
import traceback
import codecs


class Section(object):
    """Any section or sub-section or value in an input sequence"""

    def __init__(self):
        """Initialize or reset section"""
        # if not hasattr(self, "name"):
        #     self.name = "Unnamed"

        if hasattr(self, "value") and type(self.value) is list:
            self.value = []
        else:
            self.value = ""
            """Current value of the item as it appears in an InputFile"""

        self.comment = ""
        """A user-specified header and/or comment about the section"""

        if hasattr(self, "DEFAULT_COMMENT"):
            self.comment = self.DEFAULT_COMMENT

    def setattr_keep_type(self, attr_name, attr_value):
        """ Set attribute attr_name = attr_value.
            If existing value of attr_name is int, float, bool, or Enum,
            try to remove spaces and convert attr_value to the same type before setting.
            Args:
                attr_name (str): Name of attribute of self to set.
                attr_value: New value to assign to attr_name.
        """
        try:
            old_value = getattr(self, attr_name, "")
            if type(old_value) == int:
                if isinstance(attr_value, str):
                    attr_value = attr_value.replace(' ', '')
                val, val_is_good = ParseData.intTryParse(attr_value)
                if val_is_good:
                    setattr(self, attr_name, val)
            elif type(old_value) == float:
                if isinstance(attr_value, str):
                    attr_value = attr_value.replace(' ', '')
                val, val_is_good = ParseData.floatTryParse(attr_value)
                if val_is_good:
                    setattr(self, attr_name, val)
            elif isinstance(old_value, Enum):
                val_is_good = True
                if not isinstance(attr_value, Enum):
                    enum_type = type(old_value)
                    try:
                        attr_value = enum_type[attr_value.replace('-', '_')]
                    except KeyError:
                        try:
                            attr_value = enum_type[attr_value.upper().replace('-', '_')]
                        except KeyError:
                            val_is_good = False
                            print("Did not find value '" + attr_value + "' in valid values for '" + attr_name + "'")
                if val_is_good:
                    setattr(self, attr_name, attr_value)
            elif type(old_value) == bool:
                if not isinstance(attr_value, bool):
                    attr_value = str(attr_value).upper() not in ("NO", "FALSE")
                setattr(self, attr_name, attr_value)
            else:
                setattr(self, attr_name, attr_value)
        except Exception as e:
            print("Exception setting {}: {}\n{}".format(attr_name, str(e), str(traceback.print_exc())))
            setattr(self, attr_name, attr_value)
            print(str(attr_name) + " now = " + str(getattr(self, attr_name)))

    def find_item(self, aName):
        if isinstance(self.value, list):
            for obj in self.value:
                if aName.upper() == obj.name.upper():
                    return obj
        return None

    def get_item(self, fname, fvalue):
        if not isinstance(self.value, list): return None
        if not self.value or len(self.value) == 0: return None
        if not hasattr(self.value[0], fname): return None
        for obj in self.value:
            if obj.__dict__[fname] == fvalue:
                return obj
        return None


class SectionAsList(Section):
    def __init__(self, section_name, section_comment=None):
        self.value = []
        if not section_name.startswith("["):
            section_name = '[' + section_name + ']'
        self.SECTION_NAME = section_name.upper()
        if section_comment:
            self.DEFAULT_COMMENT = section_comment
        Section.__init__(self)

    def find_item(self, aName):
        if aName:
            for obj in self.value:
                if aName.upper() == obj.name.upper():
                    return obj
        return None

    def get_item(self, fname, fvalue):
        if not self.value or len(self.value) == 0: return None
        if not hasattr(self.value[0], fname): return None
        for obj in self.value:
            if obj.__dict__[fname] == fvalue:
                return obj
        return None


class SectionWriter(object):
    """ Base class for writing a section or sub-section or value to an input file """

    field_format = " {:19}\t{}"  # Default field format

    @staticmethod
    def as_text(section):
        """ Format contents of this section for writing to inp file.
            Args:
                section (Section): section of input sequence
        """
        if isinstance(section, str):
            return section
        txt = SectionWriter._get_text_using_metadata(section)
        if txt or txt == '':
            return txt
        if isinstance(section.value, str) and len(section.value) > 0:
            return section.value
        elif isinstance(section.value, (list, tuple)):
            text_list = []
            if hasattr(section, "SECTION_NAME") and section.SECTION_NAME:
                text_list.append(section.SECTION_NAME)
            if section.comment:
                text_list.append(section.comment)
            for item in section.value:
                text_list.append(str(item))
            return '\n'.join(text_list)
        elif section.value is None:
            return ''
        else:
            return str(section.value)

    @staticmethod
    def _get_text_using_metadata(section):
        """ Get input file representation of section using attributes represented in metadata, if any.
            Private method intended for use by subclasses.
            Returns empty string if the attributes in metadata have no values.
            Returns None if there is no appropriate metadata."""
        if hasattr(section, "metadata") and section.metadata:
            found_any = False
            text_list = []
            if hasattr(section, "SECTION_NAME"):
                text_list.append(section.SECTION_NAME)
            if section.comment:
                text_list.append(section.comment)
                if section.comment != getattr(section, "DEFAULT_COMMENT", ''):
                    found_any = True
            for metadata_item in section.metadata:
                attr_line = SectionWriter._get_attr_line(section, metadata_item.input_name, metadata_item.attribute)
                if attr_line:
                    text_list.append(attr_line)
                    found_any = True
            if found_any:
                return '\n'.join(text_list)
            return ''
        return None

    @staticmethod
    def _get_attr_line(section, label, attr_name):
        """ Generate one line of an input sequence which specifies the label and value of the attribute attr_name
        Args:
            section (Section): project section that may contain a value for the attribute named attr_name.
            label (str): label that will appear in the returned line.
            attr_name (str): name of attribute to get the value of. If attribute is not present, None is returned.
         """
        if label and attr_name and hasattr(section, attr_name):
            attr_value = getattr(section, attr_name)
            if isinstance(attr_value, Enum):
                attr_value = attr_value.name.replace('_', '-')
            if isinstance(attr_value, bool):
                if attr_value:
                    attr_value = "YES"
                else:
                    attr_value = "NO"
            if isinstance(attr_value, list):
                attr_value = ' '.join(attr_value)
            if attr_value or attr_value == 0:
                return SectionWriter.field_format.format(label, attr_value)
        else:
            return None

    @staticmethod
    def yes_no(true_false):
        if true_false:
            return "YES"
        else:
            return "NO"


class InputFileWriterBase(object):
    """ Base class common to SWMM and EPANET.
        Creates and saves text version of model input file *.inp.
    """
    def as_text(self, project, derived_sections):
        """
        Text version of project, suitable for saving to *.inp file.
        Args:
            project (ProjectBase): Project data to serialize as text.
            derived_sections (dict): Section names and full text to insert or append to the ones in self.sections
        Returns:
            string containing data from the specified project in *.inp format.
        """
        if derived_sections:
            # Make a local copy that we remove items from as we use them
            derived_sections = derived_sections.copy()
        section_text_list = []
        try:
            if hasattr(project, "section_order"):
                section_order = project.section_order
            else:
                section_order = None
            for section in project.sections:
                attr_name = ''
                section_name = ''
                if hasattr(section, "SECTION_NAME"):
                    section_name = section.SECTION_NAME
                    if "subcentroid" in section_name.lower() or "sublink" in section_name.lower():
                        continue
                    attr_name = "write_" + project.format_as_attribute_name(section_name)
                if section_name and "CALIBRATION" in section_name.upper():
                    # EPANET doesn't recognize [CALIBRATIONS] section
                    # it is for internal use at run time
                    continue
                if hasattr(self, attr_name):
                    writer = self.__getattribute__(attr_name)
                elif hasattr(section, "value") and isinstance(section.value, str):
                    writer = SectionWriter()
                else:
                    writer = SectionWriterAsList(section_name, SectionWriter(), None)
                try:
                    if writer.as_text(section):
                        section_text = writer.as_text(section).rstrip('\n')
                        if section_text and section_text != '[END]':                    # Skip adding blank sections
                            section_text_list.append(section_text)

                    # If we have a section order and derived sections to insert,
                    # insert any derived sections that come directly after this section.
                    if section_order and section_name and derived_sections:
                        try:
                            index = section_order.index(section_name.upper()) + 1
                            next_section = section_order[index]
                            while next_section:
                                next_derived_section = derived_sections.pop(next_section, None)
                                if next_derived_section:
                                    section_text_list.append(next_derived_section)
                                    index += 1
                                    next_section = section_order[index]
                                else:
                                    next_section = None
                        except:
                            pass
                except Exception as e1:
                    section_text_list.append(str(e1) + '\n' + str(traceback.print_exc()))
            if derived_sections is not None:
                for section_text in derived_sections.values(): #.items()
                    section_text_list.append(section_text)
            return '\n\n'.join(section_text_list) + '\n'
        except Exception as e2:
            return str(e2) + '\n' + str(traceback.print_exc())

    def write_file(self, project, file_name):
        """
        Save text file version of project in *.inp file format in file_name.
        Args:
            project (ProjectBase): Project data to serialize as text.
            file_name (str): full path and file name to save in.
        Returns:
            string containing data from the specified project in *.inp format.
        """
        if file_name:
            with open(file_name, 'w') as writer:
                writer.writelines(self.as_text(project, None))
                # project.file_name = file_name


class SectionWriterAsList(SectionWriter):
    """ Section writer that can serialize a section that contains a list of items. """
    def __init__(self, section_name, list_type_writer, section_comment):
        """
        Create a section writer that can serialize a section that contains a list of items.
        Args:
            section_name (str): Name of section. Square brackets will be added if not already present.
            list_type_writer (type or instance): Writer that can serialize items in the section.
            section_comment (str): Default comment lines that appear at the beginning of the section. Can be None.
        """
        if list_type_writer is None:
            print ("No list_type_writer specified for " + section_name)
        if not section_name.startswith("["):
            section_name = '[' + section_name + ']'
        self.SECTION_NAME = section_name.upper()
        SectionWriter.__init__(self)
        if isinstance(list_type_writer, type):
            self.list_type_writer = list_type_writer()
        else:
            self.list_type_writer = list_type_writer

        if section_comment:
            self.DEFAULT_COMMENT = section_comment

    def as_text(self, section):
        """ Format contents of this section for writing to inp file.
            Args:
                section (Section): section of input sequence that contains a list of items in its value attribute
        """
        if section.value or (section.comment and (not hasattr(section, "DEFAULT_COMMENT") or
                                                      section.comment != section.DEFAULT_COMMENT)):
            text_list = []
            if hasattr(section, "SECTION_NAME") and section.SECTION_NAME and section.SECTION_NAME != "Comment":
                text_list.append(section.SECTION_NAME)
            elif hasattr(self, "SECTION_NAME") and self.SECTION_NAME and self.SECTION_NAME != "Comment":
                text_list.append(self.SECTION_NAME)
            if section.comment:
                text_list.append(section.comment)
            elif hasattr(self, "DEFAULT_COMMENT") and self.DEFAULT_COMMENT:
                text_list.append(self.DEFAULT_COMMENT)
            if isinstance(section.value, str):
                text_list.append(section.value.rstrip('\n'))  # strip any newlines from end of each item
            else:
                for item in section.value:
                    if item is not None:
                        if hasattr(item, "description"):
                            if len(item.description) > 0 and section.SECTION_NAME != '[COORDINATES]' and \
                                                             section.SECTION_NAME != '[SUBAREAS]' and \
                                                             section.SECTION_NAME != '[LOSSES]' and \
                                                             section.SECTION_NAME != '[SYMBOLS]' and \
                                                             section.SECTION_NAME != '[STATUS]' and \
                                                             section.SECTION_NAME != '[EMITTERS]' and \
                                                             section.SECTION_NAME != '[PATTERNS]' and \
                                                             section.SECTION_NAME != '[CURVES]':
                                if item.description[0] == ';':
                                    text_list.append(item.description)
                                else:
                                    text_list.append(';' + item.description)
                        if isinstance(item, str):
                            item_str = item
                        else:
                            if hasattr(item, "SECTION_NAME") and item.SECTION_NAME == "Comment":  #xw9/13/2016
                                item_str = item.value
                            else:
                                item_str = self.list_type_writer.as_text(item)
                        if item_str is not None and item_str:
                            # Uncomment below to skip blank items unless they are a blank comment, those are purposely blank
                            # if item_str.strip() or isinstance(item, str) or
                            #  (isinstance(item, Section) and item.SECTION_NAME == "Comment"):
                            text_list.append(item_str.rstrip('\n'))  # strip any newlines from end of each item
            return '\n'.join(text_list)
        else:
            return ''


class Transects(Section):
    SECTION_NAME = "[TRANSECTS]"
    DEFAULT_COMMENT = ";;Transect Data in HEC-2 format"

    def __init__(self):
        Section.__init__(self)
        self.value = []


class Transect(Section):
    """the cross-section geometry of a natural channel or conduit with irregular shapes"""

    def __init__(self):
        Section.__init__(self)

        ## Transect Name
        self.name = ''

        ## Manning's n of left overbank portion of channel. Use 0 if no change from previous NC line.
        self.n_left = '0'

        ## Manning's n of right overbank portion of channel. Use 0 if no change from previous NC line.
        self.n_right = '0'

        ## Manning's n of main channel portion of channel. Use 0 if no change from previous NC line.
        self.n_channel = '0'

        ## station position which ends the left overbank portion of the channel (ft or m).
        self.overbank_left = '0'

        ## station position which begins the right overbank portion of the channel (ft or m).
        self.overbank_right = '0'

        ## factor by which distances between stations should be multiplied to increase (or decrease) the width of the channel (enter 0 if not applicable).
        self.stations_modifier = '0'

        ## amount added (or subtracted) from the elevation of each station (ft or m).
        self.elevations_modifier = '0'

        ## the ratio of the length of a meandering main channel to the length of the overbank area that surrounds it (use 0 if not applicable).
        self.meander_modifier = '0'

        ## list of (station, elevation) pairs
        self.stations = []


class TransectsWriter(SectionWriter):

    SECTION_NAME = "[TRANSECTS]"
    DEFAULT_COMMENT = ";;Transect Data in HEC-2 format"

    @staticmethod
    def as_text(transects):
        """Contents of this section formatted for writing to file"""
        if transects.value or (transects.comment and transects.comment != transects.DEFAULT_COMMENT):
            text_list = [transects.SECTION_NAME]
            if transects.comment:
                text_list.append(transects.comment)
            else:
                text_list.append(transects.DEFAULT_COMMENT)
            for item in transects.value:
                item_str = TransectWriter.as_text(item)
                text_list.append(item_str.rstrip('\n'))  # strip any newlines from end of each item
            return '\n'.join(text_list)
        else:
            return ''


class TransectWriter(SectionWriter):
    """the cross-section geometry of a natural channel or conduit with irregular shapes"""

    field_format_nc = "NC\t{:8}\t{:8}\t{:8}"
    field_format_x1 = "X1\t{:16}\t{:8}\t{:8}\t{:8}\t{:8}\t{:8}\t{:8}\t{:8}\t{:8}"
    field_format_gr = "\t{:8}\t{:8}"

    @staticmethod
    def as_text(transect):
        lines = []
        if len(transect.stations) > 0:
            if transect.comment:
                if transect.comment.startswith(';'):
                    lines.append(transect.comment)
                else:
                    lines.append(';' + transect.comment.replace('\n', '\n;'))
            if transect.n_left or transect.n_right or transect.n_channel:
                if len(transect.n_left) == 0:
                    transect.n_left = '0'
                if len(transect.n_right) == 0:
                    transect.n_right = '0'
                if len(transect.n_channel) == 0:
                    transect.n_channel = '0'
                if len((transect.n_left + transect.n_right + transect.n_channel).replace('.', '').replace('0', '')) > 0:
                    lines.append(TransectWriter.field_format_nc.format(transect.n_left, transect.n_right, transect.n_channel))
            lines.append(TransectWriter.field_format_x1.format(transect.name,
                                                     len(transect.stations),
                                                     transect.overbank_left,
                                                     transect.overbank_right,
                                                     "0.0", "0.0",
                                                     transect.meander_modifier,
                                                     transect.stations_modifier,
                                                     transect.elevations_modifier))
            line = "GR"
            stations_this_line = 0
            for station in transect.stations:
                line += TransectWriter.field_format_gr.format(station[0], station[1])
                stations_this_line += 1
                if stations_this_line > 4:
                    lines.append(line)
                    line = "GR"
                    stations_this_line = 0
            if stations_this_line > 0:
                lines.append(line)

        return '\n'.join(lines)


class LossWriter(SectionWriter):
    """Convert minor head loss coefficients, flap gates, and seepage rates for a conduit into text."""

    field_format = "{:16}\t{:10}\t{:10}\t{:10}\t{:10}\t{:10}"

    @staticmethod
    def as_text(conduit):
        """format conduit loss information for writing to file"""
        # if conduit.name and (conduit.entry_loss_coefficient
        #                      or conduit.exit_loss_coefficient
        #                      or conduit.loss_coefficient
        #                      or conduit.seepage):
        return LossWriter.field_format.format(conduit.name,
                                              conduit.entry_loss_coefficient,
                                              conduit.exit_loss_coefficient,
                                              conduit.loss_coefficient,
                                              SectionWriter.yes_no(conduit.flap_gate),
                                              conduit.seepage)
        # else:
        #     return None

class InputFileReader(object):
    """ Base class for reading input files """
    def __init__(self):
        self.input_err_msg = ""

    def read_file(self, project, file_name):
        """ Read the contents of file_name into project. """
        self.input_err_msg = ""
        try:
            """
            with open(file_name, 'r') as inp_reader:
                project.file_name = file_name
                self.set_from_text_lines(project, inp_reader.readlines())
            """
            with codecs.open(file_name, 'r', 'utf-8') as inp_reader:
                project.file_name = file_name
                self.set_from_text_lines(project, inp_reader.readlines())
                """
                task = TaskOpenInput('open file', project, inp_reader.readlines(), self.read_section)
                task.begun.connect(lambda: print('reading begins...'))
                task.progressChanged.connect(lambda: print(task.progress()))
                task.taskCompleted.connect(lambda: self.finished_reading(project))
                task.run()
                """
        except Exception as e:
            # print("Error reading {0}: {1}\n{2}".format(file_name, str(e), str(traceback.print_exc())))
            try:
                with codecs.open(file_name, 'r', 'latin1') as inp_reader:
                    project.file_name = file_name
                    # self.set_from_text_lines(project, iter(inp_reader))
                    self.set_from_text_lines(project, inp_reader.readlines())
            except Exception as e:
                self.input_err_msg = "File is probably not a valid project or input file."
                print("Error reading {0}: {1}\n{2}".format(file_name, str(e), str(traceback.print_exc())))
                if ".net" in file_name:
                    self.input_err_msg += "\nPlease note: binary (.net) input file is deprecated (not supported)."

    def set_from_text_lines(self, project, lines_iterator):
        """Read a project file from lines of text.
            Args:
                project (ProjectBase): Project object to read data into
                lines_iterator (iterator): Lines of text formatted as input file.
        """
        project.sections = []
        project.section_order = []
        section_name = ""
        section_whole = []
        total_count = len(lines_iterator)
        line_ctr = 1
        for line in lines_iterator:
            if line.lstrip().startswith('['):
                if section_name:
                    project.section_order.append(section_name.upper())
                    self.read_section(project, section_name, '\n'.join(section_whole))
                section_name = line.strip()
                section_whole = [section_name]
            elif line.strip():
                section_whole.append(line.rstrip())
            line_ctr = line_ctr + 1

        if section_name:
            project.section_order.append(section_name.upper())
            self.read_section(project, section_name, '\n'.join(section_whole))
        project.add_sections_from_attributes()  # if there are any sections not in the file, add them to list
        self.finished_reading(project)

    def finished_reading(self, project):
        print ("Finished reading " + project.file_name)

    def read_section(self, project, section_name, section_text):
        """ Read the section named section_name whose complete text is section_text into project. """

        old_section = project.find_section(section_name)
        #if old_section:
        #    project.sections.remove(old_section)
        new_section = None
        attr_name = project.format_as_attribute_name(section_name)

        # special case for section 'lid_controls', because of multi-line structure, must strip out comment lines
        if attr_name == "lid_controls":
            # strip comment lines from section_text
            section_text_list = section_text.split('\n')
            string_without_comments = ""
            for line in section_text_list:
                if line[0] != ";":
                    string_without_comments += line + '\n'
            section_text = string_without_comments[:-1]

        reader_name = "read_" + attr_name
        if hasattr(self, reader_name):
            reader = self.__getattribute__(reader_name)
            try:
                new_section = reader.read(section_text)
            except Exception as e:
                print("Exception calling " + reader_name + " for " + section_name + ":\n" + str(e) +
                      '\n' + str(traceback.print_exc()))

        if new_section is None:
            if not section_name == '[END]':
                self.input_err_msg += '\n' + 'Unrecognized keyword (' + section_name + ').'
            print("Default Section for " + section_name)
            new_section = Section()
            new_section.SECTION_NAME = section_name
            if not section_name == section_text:
                new_section.value = section_text

        if "REACTION" in new_section.SECTION_NAME.upper() and old_section:
            for vmdata in old_section.metadata:
                old_section.__setattr__(vmdata.attribute, new_section.__getattribute__(vmdata.attribute))
            if new_section.value and len(new_section.value) > 0:
                for spec in new_section.value:
                    old_section.value.append(spec)
        else:
            project.__setattr__(attr_name, new_section)

        if old_section is None: #new_section not in project.sections:
            project.sections.append(new_section)


class SectionReader(object):
    """ Read a section or sub-section or value in an input file """

    def __init__(self):
        """Initialize section reader"""
        self.section_type = Section

    def read(self, new_text):
        """Read properties from text.
            Args:
                new_text (str): Text to parse into properties.
        """
        section = self.section_type()
        section.value = new_text
        for line in new_text.splitlines():
            self.set_text_line(section, line)
        return section

    @staticmethod
    def set_comment_check_section(section, line):
        """ Set comment to text after a semicolon and return the rest of the line.
            If the line is a section header (starts with open square bracket) then check against SECTION_NAME.
            If it matches, return empty string. If it does not match, raise ValueError.
            Args:
                section (Section): Section of input file to populate
                line (str): Text to search for a comment or section name.
        """
        comment_split = line.split(';', 1)
        if len(comment_split) == 2:  # Found a comment
            line = comment_split[0]
            this_comment = ';' + comment_split[1]
            #if section.value:
            if hasattr(section, "comment") and section.comment:
                # # Compare with existing comment and decide whether to discard one or combine them
                # omit_chars = " ;\t-_"
                # this_stripped = SectionReader.omit_these(this_comment, omit_chars).upper()
                # if len(this_stripped) == 0 and ("---" in this_comment) and not ("---" in section.comment):
                #     section.comment += '\n'  # Add dashed line on a new line if comment does not already have one
                # elif this_stripped in SectionReader.omit_these(section.comment, omit_chars).upper():
                #     this_comment = ''  # Already have this comment, don't add it again
                # elif hasattr(section, "DEFAULT_COMMENT") and section.comment == section.DEFAULT_COMMENT:
                #     section.comment = ''  # Replace default comment with the one we are reading
                # else:
                if not this_comment.lower() in section.comment.lower():
                    section.comment += '\n' + this_comment  # Separate from existing comment with newline
            elif hasattr(section, "description"):
                if not this_comment.lower() in section.description.lower():
                    if len(section.description) == 0:
                        section.description = this_comment
                    else:
                        section.description += '\n' + this_comment  # Separate from existing comment with newline
            else:
                section.comment = this_comment
                # section.description = this_comment
        if line.startswith('['):
            if hasattr(section, "SECTION_NAME") and line.strip().upper() != section.SECTION_NAME.upper():
                raise ValueError("Cannot set " + section.SECTION_NAME + " from: " + line.strip())
            else:  # subsection does not have a SECTION_NAME or SECTION_NAME matches: no further processing needed
                line = ''
        return line  # Return the portion of the line that was not in the comment and was not a section header

    @staticmethod
    def omit_these(original, omit_chars):
        """Return original with any characters in omit_chars removed.
            Args:
                original (str): Text to search
                omit_chars (str): Characters to remove from original
        """
        return ''.join(c for c in original if c not in omit_chars)

    @staticmethod
    def set_text_line(section, line):
        """Set part of this section from one line of text.
            Args:
                section (Section): Section of input file to populate
                line (str): One line of text formatted as input file.
        """
        line = SectionReader.set_comment_check_section(section, line)
        if line.strip():
            # Set fields from metadata if this section has metadata
            attr_name = ""
            attr_value = ""
            tried_set = False
            if hasattr(section, "metadata") and section.metadata:
                (attr_name, attr_value) = SectionReader.get_attr_name_value(section, line)
            else:  # This section does not have metadata, try to set its fields anyway
                line_list = line.split()
                if len(line_list) > 1:
                    if len(line_list) == 2:
                        test_attr_name = line_list[0].lower()
                        if hasattr(section, test_attr_name):
                            attr_name = test_attr_name
                            attr_value = line_list[1]
                    else:
                        for value_start in (1, 2):
                            for connector in ('', '_'):
                                test_attr_name = connector.join(line_list[:value_start]).lower()
                                if hasattr(section, test_attr_name):
                                    attr_name = test_attr_name
                                    attr_value = ' '.join(line_list[value_start:])
                                    break
            if attr_name:
                try:
                    tried_set = True
                    section.setattr_keep_type(attr_name, attr_value)
                except:
                    print("Section.text could not set " + attr_name)
            if not tried_set:
                print("Section.text skipped: " + line)

    @staticmethod
    def get_attr_name_value(section, line):
        """Search metadata of section for attribute with input_name matching start of line.
            Args:
                section (Section): data class
                line (str): One line of text formatted as input file, with field name followed by field value.
            Returns:
                Attribute name from metadata and new attribute value from line as a tuple:
                (attr_name, attr_value) or (None, None) if not found.
        """
        search_metadata = []
        if hasattr(section, "metadata") and section.metadata:
            search_metadata.append(section.metadata)
        # if hasattr(self, "metadata") and self.metadata:
        #     search_metadata.append(self.metadata)
        if search_metadata:
            lower_line = line.lower().strip()
            for metadata in search_metadata:
                for meta_item in metadata:
                    key = meta_item.input_name.lower()
                    if len(lower_line) > len(key):
                        # if this line starts with this key followed by a space or tab
                        if lower_line.startswith(key) and lower_line[len(key)] in (' ', '\t'):
                            if hasattr(section, meta_item.attribute):
                                # return attribute name and value specified on this line
                                return meta_item.attribute, line.strip()[len(key) + 1:].strip()
        return None, None


class SectionReaderAsList(SectionReader):
    """ Section reader that reads a section that contain a list of items """
    def __init__(self, section_name, list_type_reader, default_comment=None):
        if not section_name.startswith("["):
            section_name = '[' + section_name + ']'
        self.SECTION_NAME = section_name.upper()
        SectionReader.__init__(self)
        if isinstance(list_type_reader, type):
            self.list_type_reader = list_type_reader()
        else:
            self.list_type_reader = list_type_reader
        if default_comment:
            self.DEFAULT_COMMENT = default_comment

    def _init_section(self):
        section = self.section_type()
        # Set new section's SECTION_NAME if it has not already been set
        if not hasattr(section, "SECTION_NAME") and hasattr(self, "SECTION_NAME") and self.SECTION_NAME:
            section.SECTION_NAME = self.SECTION_NAME

        # TODO: figure out best way to tell whether this section can be indexed by name. For now we hard code names:
        index_these = ["[COORDINATES]", "[POLYGONS]", "[VERTICES]", "[SYMBOLS]", "[RAINGAGES]", "[SUBCATCHMENTS]",
                       "[HYDROGRAPHS]", "[LID_CONTROLS]", "[AQUIFERS]", "[SNOWPACKS]",
                       "[JUNCTIONS]", "[OUTFALLS]", "[DIVIDERS]", "[STORAGE]",
                       "[CONDUITS]", "[PUMPS]", "[ORIFICES]", "[WEIRS]", "[LANDUSES]", "[POLLUTANTS]",
                       "[PATTERNS]", "[CURVES]", "[TIMESERIES]", "[LABELS]", "[EVENTS]"]
        if hasattr(section, "SECTION_NAME") and section.SECTION_NAME in index_these:
            section.value = IndexedList([], ['name'])
        else:
            section.value = []
        return section

    def read(self, new_text):
        section = self._init_section()
        comment = ''
        keep_per_item_comment = True
        new_text = new_text.encode('ascii', errors='ignore')  # strip out non-ascii characters
        new_text = str(new_text, 'utf-8', 'ignore')
        if new_text.startswith('[LANDUSE'):
            keep_per_item_comment = True
        new_text = new_text.lstrip()  # xw20170328, remove heading white spaces indluing /n /t and spaces
        for line in new_text.splitlines()[1:]:  # process each line after the first one [section name]
            # if row starts with semicolon or is blank, add as a comment
            if line.lstrip().startswith(';') or not line.strip():
                if section.value or len(comment) > 0:  # If we have already added items to this section, add comment as a Section
                    # comment += line  xw20170327
                    if len(comment) > 0:  # xw20170327, added \n for multiple lines of comments within a section
                        comment += "\n" + line
                    else:
                        comment += line
                else:  # If we are still at the beginning of the section, set comment instead of adding a Section
                    if line.startswith(';;'):
                        self.set_comment_check_section(section, line)
                    elif keep_per_item_comment and line.startswith(';'):
                        comment = line
            else:
                if keep_per_item_comment and comment:
                    line = line + ' ' + comment
                    comment = ''
                self.read_item(section, line)
        return section

    def read_item(self, section, text):
        try:
            if self.list_type_reader:
                make_one = self.list_type_reader.read(text)
                if len(section.value) == 0:
                    if hasattr(make_one, "name"):
                        section.value = IndexedList([], ['name'])
            else:
                make_one = text

            if make_one is not None:
                section.value.append(make_one)
        except Exception as e:
            print("Could not create object from: " + text + '\n' + str(e) + '\n' + str(traceback.print_exc()))


class SectionReaderAsListGroupByID(SectionReaderAsList):
    """
    Reader for a section that contains items which may each span more than one line.
    Each item includes zero or more comment lines and one or more lines with the first field being the item ID.
    """

    def read(self, new_text):
        """
        Read a Section that contains items which may each span more than one line.
        Each item includes zero or more comment lines and one or more lines with the first field being the item ID.

        Parse new_text into a section comment (column headers) followed by items created by self.list_type_reader.
        section.value is created as a list of items read from new_text.
            Args:
                new_text (str): Text of whole section to parse into comments and a list of items.
            Returns:
                new self.section_type with value attribute populated from items in new_text.
        """
        section = self._init_section()
        lines = new_text.splitlines()
        self.set_comment_check_section(section, lines[0])  # Check first line against section name
        next_index = 1
        # expected_comment_lines = section.comment.splitlines()
        # for line_number in range(1, len(expected_comment_lines) + 1):  # Parse initial comment lines into comment
        #     if str(lines[line_number]).startswith(';'):
        #         # On multi-line initial comment, make sure last line is just dashes if the default comment was.
        #         # Otherwise it is kept out of the section comment and will be assigned to go with an item.
        #         if next_index < expected_comment_lines \
        #                 or len(Section.omit_these(lines[line_number], ";-_ \t")) == 0 \
        #                 or len(Section.omit_these(expected_comment_lines[line_number - 1], ";-_ \t")) > 0:
        #             self.set_comment_check_section(section, lines[line_number])
        #             next_index += 1
        #     else:
        #         break

        for next_index in range(1, len(lines) - 1):
            if not lines[next_index].strip().startswith(';'):
                break

        # If last comment line is not just a separator line, it is kept as the first item comment.
        if len(SectionReader.omit_these(lines[next_index-1], ";-_ \t")) > 0:
            next_index -= 1

        item_text = ""
        item_name = ""
        for line in lines[next_index:]:
            if line.startswith(';'):  # Found a comment, must be the start of a new item
                if len(item_name) > 0:
                    self.read_item(section, item_text)
                    item_text = ''
                elif item_text:
                    item_text += '\n'
                item_text += line
                item_name = ''
            else:
                id_split = line.split()
                if len(id_split) > 1:
                    new_item_name = id_split[0].strip()
                    if len(item_name) > 0:  # If we already read an ID that has not been saved to value yet
                        if new_item_name != item_name:  # If this item is not the same one we are already reading
                            self.read_item(section, item_text)
                            item_text = ''  # clear the buffer after using it to create/append an item
                    item_name = new_item_name
                    if item_text:
                        item_text += '\n'
                    item_text += line
        if item_text:
            self.read_item(section, item_text)
        return section


class TransectsReader(SectionReader):

    SECTION_NAME = "[TRANSECTS]"
    DEFAULT_COMMENT = ";;Transect Data in HEC-2 format"

    @staticmethod
    def read(new_text):
        transects = Transects()
        transects.value = IndexedList([], ['name'])
        item_lines = []
        line = ''
        comment = ''
        n_left, n_right, n_channel = 0, 0, 0
        for line in new_text.splitlines():
            line = line.lstrip()
            if line.startswith(";;") or line.startswith('['):
                SectionReader.set_comment_check_section(transects, line)
            elif line.startswith(';'):
                comment = line
            elif not line.strip():  # add blank row as a comment item in transects.value list
                comment = Section()
                comment.name = "Comment"
                comment.value = ''
                # transects.value.append(comment)
            else:
                fields = line.split()
                if len(fields) > 2:
                    token = fields[0].upper()
                    if token == "GR":
                        for elev_index in range(1, len(fields) - 1, 2):
                            transect.stations.append((fields[elev_index], fields[elev_index + 1]))
                    elif len(fields) > 3:
                        if token == "NC":
                            n_left, n_right, n_channel = fields[1:4]
                        elif token == "X1":
                            transect = Transect()
                            transect.comment = comment
                            comment = ''
                            transect.n_left = n_left
                            transect.n_right = n_right
                            transect.n_channel = n_channel
                            transect.name = fields[1]
                            transect.overbank_left = fields[3]
                            if len(fields) > 4:
                                transect.overbank_right = fields[4]
                            if len(fields) > 7:
                                transect.meander_modifier = fields[7]
                            if len(fields) > 8:
                                transect.stations_modifier = fields[8]
                            if len(fields) > 9:
                                transect.elevations_modifier = fields[9]
                            transects.value.append(transect)
        return transects


class TransectReader(SectionReader):
    """the cross-section geometry of a natural channel or conduit with irregular shapes"""


    @staticmethod
    def read(new_text):
        transect = Transect()
        for line in new_text.splitlines():
            line = SectionReader.set_comment_check_section(transect, line)
            fields = line.split()
            if len(fields) > 2:
                if fields[0].upper() == "GR":
                    for elev_index in range(1, len(fields) - 1, 2):
                        transect.stations.append((fields[elev_index], fields[elev_index + 1]))
                elif len(fields) > 3:
                    if fields[0].upper() == "NC":
                        (transect.n_left, transect.n_right, transect.n_channel) = fields[1:4]
                    elif fields[0].upper() == "X1":
                        transect.name = fields[1]
                        transect.overbank_left = fields[3]
                        if len(fields) > 4:
                            transect.overbank_right = fields[4]
                        if len(fields) > 7:
                            transect.meander_modifier = fields[7]
                        if len(fields) > 8:
                            transect.stations_modifier = fields[8]
                        if len(fields) > 9:
                            transect.elevations_modifier = fields[9]
        return transect


class ParseData:
    @staticmethod
    def intTryParse(value):
        try:
            if isinstance(value, int):
                return value, True
            else:
                if str(value):
                    if "null" in str(value).lower():
                        return value, False
                    return int(value), True
                else:
                    return None, False
        except ValueError:
            return value, False

    @staticmethod
    def floatTryParse(value):
        try:
            if isinstance(value, float):
                return value, True
            else:
                if str(value):
                    if "null" in str(value).lower():
                        return value, False
                    return float(value), True
                else:
                    return None, False
        except ValueError:
            return value, False


class IndexedList(list):
    """
    Class that combines a list and a dict into a single class
     - Written by Hugh Bothwell (http://stackoverflow.com/users/33258/hugh-bothwell)
     - Original source available at:
          http://stackoverflow.com/questions/5332841/python-list-dict-property-best-practice/5334686#5334686
     - Modifications by Jeff Terrace
    Given an object, obj, that has a property x, this allows you to create an IndexedList like so:
       L = IndexedList([], ('x'))
       o = obj()
       o.x = 'test'
       L.append(o)
       L[0] # = o
       L['test'] # = o
    """
    def __init__(self, items, attrs):
        super(IndexedList, self).__init__(items)
        # do indexing
        self._attrs = tuple(attrs)
        self._index = {}
        _add = self._addindex
        for obj in self:
            _add(obj)

    def _addindex(self, obj):
        _idx = self._index
        for attr in self._attrs:
            _idx[getattr(obj, attr)] = obj

    def _delindex(self, obj):
        _idx = self._index
        for attr in self._attrs:
            try:
                del _idx[getattr(obj, attr)]
            except KeyError:
                pass

    def __delitem__(self, ind):
        try:
            obj = list.__getitem__(self, ind)
        except (IndexError, TypeError):
            obj = self._index[ind]
            ind = list.index(self, obj)
        self._delindex(obj)
        return list.__delitem__(self, ind)

    def __delslice__(self, i, j):
        for ind in range(i, j):
            self.__delitem__(ind)

    def __getitem__(self, ind):
        try:
            return self._index[ind]
        except (KeyError, TypeError):
            if isinstance(ind, str):
                raise
            try:
                return list.__getitem__(self, ind)
            except Exception as ex:
                raise Exception("Could not find key/index '" + str(ind) + "' in IndexedList: " + str(ex))

    def get(self, key, default=None):
        try:
            return self._index[key]
        except KeyError:
            return default

    def __contains__(self, item):
        if item in self._index:
            return True
        return list.__contains__(self, item)

    def __getslice__(self, i, j):
        return IndexedList(list.__getslice__(self, i, j), self._attrs)

    def __setitem__(self, ind, new_obj):
        try:
            obj = list.__getitem__(self, ind)
        except (IndexError, TypeError):
            obj = self._index[ind]
            ind = list.index(self, obj)
        self._delindex(obj)
        self._addindex(new_obj)
        return list.__setitem__(ind, new_obj)

    def __setslice__(self, i, j, newItems):
        _get = self.__getitem__
        _add = self._addindex
        _del = self._delindex
        # remove indexing of items to remove
        for ind in range(i, j):
            _del(_get(ind))
        # add new indexing
        if isinstance(newItems, IndexedList):
            self._index.update(newItems._index)
        else:
            for obj in newItems:
                _add(obj)
        # replace items
        return list.__setslice__(self, i, j, list(newItems))

    def append(self, obj):
        self._addindex(obj)
        return list.append(self, obj)

    def extend(self, newList):
        newList = list(newList)
        if isinstance(newList, IndexedList):
            self._index.update(newList._index)
        else:
            _add = self._addindex
            for obj in newList:
                _add(obj)
        return list.extend(self, newList)

    def insert(self, ind, new_obj):
        # ensure that ind is a numeric index
        try:
            obj = list.__getitem__(self, ind)
        except (IndexError, TypeError):
            obj = self._index[ind]
            ind = list.index(self, obj)
        self._addindex(new_obj)
        return list.insert(self, ind, new_obj)

    def pop(self, ind= -1):
        # ensure that ind is a numeric index
        try:
            obj = list.__getitem__(self, ind)
        except (IndexError, TypeError):
            obj = self._index[ind]
            ind = list.index(self, obj)
        self._delindex(obj)
        return list.pop(self, ind)

    def remove(self, ind_or_obj):
        try:
            obj = self._index[ind_or_obj]
            ind = list.index(self, obj)
        except KeyError:
            ind = list.index(self, ind_or_obj)
            obj = list.__getitem__(self, ind)
        self._delindex(obj)
        return list.remove(self, obj)


class ProjectBase(object):
    """
    Base class of SWMM and EPANET project classes that hold the data in an input sequence.
    Reading and writing the input sequence is handled in other classes.
    """

    def __init__(self):
        self.file_name = ""
        self.file_name_temporary = ""
        self.sections = []
        self.metric = False  # Both project types default to CFS, so metric defaults to False
        self.add_sections_from_attributes()

    def add_sections_from_attributes(self):
        """Add the sections that are attributes of the class to the list of sections."""
        for attr_value in vars(self).values():
            if isinstance(attr_value, Section) and attr_value not in self.sections:
                self.sections.append(attr_value)

    def find_section(self, section_name):
        """ Find an element of self.sections by name, ignoring square brackets and capitalization.
            Args:
                 section_name (str): Name of section to find.
        """
        compare_title = self.format_as_attribute_name(section_name).replace('_', '')
        if compare_title == 'timepatterns':
            compare_title = 'patterns'
        elif compare_title == 'unithydrographs':
            compare_title = 'hydrographs'
        elif compare_title == 'lidcontrols':
            compare_title = 'lid_controls'
        elif compare_title == 'lidusage':
            compare_title = 'lid_usage'

        for section in self.sections:
            this_section_name = ''
            if hasattr(section, "SECTION_NAME"):
                this_section_name = section.SECTION_NAME
            elif hasattr(section, "name"):
                this_section_name = section.name
            if this_section_name and self.format_as_attribute_name(str(this_section_name)) == compare_title:
                return section
        return None

    @staticmethod
    def format_as_attribute_name(name):
        """
        Format a name into a string that can be used as a Python attribute name.
        @param name (str) version of section or attribute name that may contain spaces (as in text input file)
        Returns (str) lowercase name with underscores instead of spaces and without square brackets.
        """
        return name.lower().replace(' ', '_').replace('[', '').replace(']', '')

    def all_nodes(self):
        lst_all = IndexedList([], ['name'])
        for section in self.nodes_groups():
            lst_all.extend(section.value)
        return lst_all

    def all_links(self):
        lst_all = IndexedList([], ['name'])
        for section in self.links_groups():
            lst_all.extend(section.value)
        return lst_all

    def find_link(self, link_name):
        for link_group in self.links_groups():
            if link_group and link_group.value:
                possible_match = link_group.find_item(link_name)
                if possible_match:
                    return possible_match
        return None

    def find_node(self, node_name):
        if node_name is None or not isinstance(node_name, str) or node_name == '':
            return None
        for node_group in self.nodes_groups():
            if node_group.value and len(node_group.value) > 0:
                existing_node = node_group.find_item(node_name)
                if existing_node is not None:
                    return existing_node
        return None

    def all_vertices(self, set_names=False):
        """ Return a list of Coordinate objects, one for each internal vertices of all links.
            If set_names is True, also set the name of each vertex to match its link. """
        lst_all = []
        for section in self.links_groups():
            for link in section.value:
                if set_names:
                    for vertex in link.vertices:
                        vertex.name = link.name
                lst_all.extend(link.vertices)
        return lst_all


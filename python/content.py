# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library

# Import from lpod
from utils import _check_arguments, _generate_xpath_query
from utils import _check_position_or_name, _get_cell_coordinates
from xmlpart import odf_element, odf_xmlpart, LAST_CHILD


class odf_content(odf_xmlpart):

    # Is it? (and won't apply to automatic styles, font declarations...)
    body_xpath = '//office:text'


    #
    # Sections
    #

    def get_section_list(self, style=None, context=None):
        return self.__get_element_list('text:section', style=style,
                                       context=context)


    def get_section(self, position, context=None):
        return self.__get_element('text:section', position, context=context)


    #
    # Paragraphs
    #

    def get_paragraph_list(self, style=None, context=None):
        return self.__get_element_list('text:p', style=style,
                                       context=context)


    def get_paragraph(self, position, context=None):
        return self.__get_element('text:p', position, context=context)


    #
    # Span
    #

    def get_span_list(self, style=None, context=None):
        return self.__get_element_list('text:span', style=style,
                                       context=context)


    def get_span(self, position, context=None):
        return self.__get_element('text:span', position, context=context)


    #
    # Headings
    #

    def get_heading_list(self, style=None, level=None, context=None):
        if level is not None:
            _check_arguments(level=level)
            attributes = {'text:outline-level': level}
        else:
            attributes = None
        return self.__get_element_list('text:h', style=style,
                                       attributes=attributes,
                                       context=context)


    def get_heading(self, position, level=None, context=None):
        if level is not None:
            _check_arguments(level=level)
            attributes = {'text:outline-level': level}
        else:
            attributes = None
        return self.__get_element('text:h', position, attributes=attributes,
                                  context=context)


    #
    # Frames
    #

    def get_frame_list(self, style=None, context=None):
        return self.__get_element_list('draw:frame', frame_style=style,
                                       context=context)


    def get_frame(self, position=None, name=None, context=None):
        _check_position_or_name(position, name)
        attributes = {'draw:name': name} if name is not None else {}
        return self.__get_element('draw:frame', position,
                                  attributes=attributes,
                                  context=context)


    #
    # Images
    #

    def __insert_image(self, element, context, xmlposition, offset):
        # XXX If context is None
        #     => auto create a frame with the good dimensions
        if context is None:
            raise NotImplementedError

        self.__insert_element(element, context, xmlposition, offset)


    def get_image(self, position=None, name=None, context=None):
        # Automatically get the frame
        frame = self.get_frame(position, name, context)
        return self.__get_element('draw:image', context=frame)


    #
    # Tables
    #

    def get_table_list(self, style=None, context=None):
        return self.__get_element_list('table:table', style=style,
                                       context=context)


    def get_table(self, position=None, name=None, context=None):
        _check_position_or_name(position, name)
        attributes = {'table:name': name} if name is not None else {}
        return self.__get_element('table:table', position,
                                  attributes=attributes, context=context)


    def get_row_list(self, style=None, context=None):
        return self.__get_element_list('table:table-row', style=style,
                                       context=context)


    #
    # Cells
    #

    def get_cell_list(self, style=None, context=None):
        return self.__get_element_list('table:table-cell', style=style,
                                       context=context)


    # Warning: This function gives just a "read only" odf_element
    def get_cell(self, name, context):
        # The coordinates of your cell
        x, y = _get_cell_coordinates(name)

        # First, we must find the good row
        cell_y = 0
        for row in self.get_row_list(context=context):
            repeat = row.get_attribute('table:number-rows-repeated')
            repeat = int(repeat) if repeat is not None else 1
            if cell_y + 1 <= y and y <= (cell_y + repeat):
                break
            cell_y += repeat
        else:
            raise IndexError, 'I cannot find cell "%s"' % name

        # Second, we must find the good cell
        cell_x = 0
        for cell in self.get_cell_list(context=row):
            repeat = cell.get_attribute('table:number-columns-repeated')
            repeat = int(repeat) if repeat is not None else 1
            if cell_x + 1 <= x and x <= (cell_x + repeat):
                break
            cell_x += repeat
        else:
            raise IndexError, 'i cannot find your cell "%s"' % name

        return cell


    #
    # Notes
    #

    def get_note_list(self, note_class=None, context=None):
        _check_arguments(note_class=note_class)
        if note_class is not None:
            attributes = {'text:note-class': note_class}
        else:
            attributes = None
        return self.__get_element_list('text:note', attributes=attributes,
                                       context=context)


    def get_note(self, id, context=None):
        attributes = {'text:id': id}
        return self.__get_element('text:note', attributes=attributes,
                                  context=context)


    def insert_note_body(self, element, context):
        body = context.get_element_list('//text:note-body')[-1]
        body.insert_element(element, LAST_CHILD)


    #
    # Annotations
    #

    def get_annotation_list(self, creator=None, start_date=None,
                            end_date=None, context=None):
        """XXX end date is not included (as expected in Python).
        """
        _check_arguments(creator=creator, start_date=start_date,
                         end_date=end_date)
        annotations = []
        for annotation in self.__get_element_list('office:annotation',
                                                  context=context):
            if creator is not None and creator != annotation.get_creator():
                continue
            date = annotation.get_date()
            if start_date is not None and date < start_date:
                continue
            if end_date is not None and date >= end_date:
                continue
            annotations.append(annotation)
        return annotations


    def get_annotation(self, creator=None, start_date=None, end_date=None,
                       context=None):
        annotations = self.get_annotation_list(creator=creator,
                start_date=start_date, end_date=end_date, context=context)
        if not annotations:
            return None
        return annotations[0]


    #
    # Styles
    #

    def get_style_list(self, family=None, category=None):
        _check_arguments(family=family)
        attributes = {}
        if family is not None:
            attributes['style:family'] = family
        query = _generate_xpath_query('style:style', attributes=attributes)
        context = self.get_category_context(category)
        if context is None:
            return self.get_element_list(query)
        else:
            return context.get_element_list(query)


    def get_style(self, name_or_element, family):
        _check_arguments(family=family)
        if isinstance(name_or_element, odf_element):
            if not name_or_element.is_style():
                raise ValueError, "element is not a style element"
        elif type(name_or_element) is str:
            attributes = {'style:name': name_or_element,
                          'style:family': family}
            query = _generate_xpath_query('style:style',
                                          attributes=attributes)
            context = self.get_element('//office:automatic-styles')
            return context.get_element(query)
        raise TypeError, "style name or element expected"
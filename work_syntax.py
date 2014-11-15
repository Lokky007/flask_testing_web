# -*- coding: utf8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import generators

from markdown.preprocessors import Preprocessor
from markdown.extensions import Extension
import re


class WorkSyntaxPreprocessor(Preprocessor):
    def run(self, lines):

        repeat = 0
        new_lines = []

        task = re.compile('^::task (.+)$')
        date = re.compile('^::date (.+)$')
        op = re.compile('^::open')
        num = re.compile('^::number (.+)$')
        lb_f = re.compile('^:- (.+)$')
        lb_t = re.compile('^:\+ (.+)$')

        match_par = re.compile('^\$(.+)\$')
        questions = re.compile('^:')

        for line in lines:
            match_task = task.search(line)
            match_date = date.search(line)
            match_op = op.search(line)
            match_number = num.search(line)
            match_false = lb_f.search(line)
            match_true = lb_t.search(line)
            match_question = questions.search(line)

            if match_task:
                new_lines.append('<h2>{0}</h2></optgroup>'
                                 .format(match_task.group(1)))
            elif match_date:
                new_lines.append('<h5>{0}</h5>'
                                 .format(match_date.group(1)))
            elif match_op:
                new_lines.append('''<br><textarea name="text1" cols="40" rows="3">
                                 </textarea>''')

            elif match_number:
                new_lines.append('''<br><input type="text"
                                name="jmeno" value="">'''
                                 .format(match_number.group(1)))

            elif match_false:
                new_lines.append('''<br><input type="radio" name="stejne_jmeno"
                                 value="{0}">{0}'''
                                 .format(match_false.group(1)))

            elif match_true:
                new_lines.append('''<br><input type="radio" name="stejne_jmeno"
                                 value="{0}">{0}'''
                                 .format(match_true.group(1)))

            elif not match_question:

                for word in line.split():
                    match8 = match_par.search(word)
                    if match8:
                        new_lines.append('{0}'.format(match8.group(1)))
                    else:
                        new_lines.append(word)
            else:
                new_lines.append(line)
        return new_lines

class WorkSyntax(Extension):
    def extendMarkdown(self, md, md_globals):
        md.preprocessors.add('urlify', WorkSyntaxPreprocessor(md), '_end')

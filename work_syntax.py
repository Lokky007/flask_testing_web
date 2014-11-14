from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import generators

from markdown.preprocessors import Preprocessor
from markdown.extensions import Extension
import re


class WorkSyntaxPreprocessor(Preprocessor):
    def run(self, lines):
        task = re.compile('^::task (.+)$')
        new_lines = []
        for line in lines:
            match = task.search(line)
            if match:
                new_lines.append('<h2>{0}</h2>'.format(match.group(1) ))
            else:
                new_lines.append(line)
        return new_lines


class WorkSyntax(Extension):
    def extendMarkdown(self, md, md_globals):
        md.preprocessors.add('urlify', WorkSyntaxPreprocessor(md), '_end')

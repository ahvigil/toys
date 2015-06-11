#!/usr/bin/env python
"""
font-awesome latex .sty file generator to create LaTeX package files
based on the fontawesome latex package at
http://www.ctan.org/tex-archive/fonts/fontawesome
but with expanded support for newer icons

useage: python falatex.py [font-awesome.css]

@author Arthur Vigil
@date 9/8/14
"""

import re, os.path, sys
import urllib2

FA_URL = "https://raw.githubusercontent.com/FortAwesome/Font-Awesome/master/css/font-awesome.css"

# use existing package text to start out 
INTRO = """
%% start of file `fontawesome.sty'.
%% Copyright 2013 Xavier Danaux (xdanaux@gmail.com).
%
% This work may be distributed and/or modified under the
% conditions of the LaTeX Project Public License version 1.3c,
% available at http://www.latex-project.org/lppl/.


%-------------------------------------------------------------------------------
%                identification
%-------------------------------------------------------------------------------
\NeedsTeXFormat{LaTeX2e}
\ProvidesPackage{fontawesome}[2013/05/10 v3.1.1 font awesome icons]


%-------------------------------------------------------------------------------
%                requirements
%-------------------------------------------------------------------------------
\usepackage{fontspec}


%-------------------------------------------------------------------------------
%                implementation
%-------------------------------------------------------------------------------

% definition of \FA as a shortcut to load the Font Awesome font
\\newfontfamily{\FA}{FontAwesome}

% generic command to display an icon by its name
\\newcommand*{\\faicon}[1]{%
  {\FA\csname faicon@#1\endcsname}}

% icon-specific commands
"""
    
out = open('fontawesome.sty','w')
out.write(INTRO)

stylesheet = urllib2.urlopen(FA_URL)
fa = stylesheet.read()

for match in re.finditer(".fa-(.*):before {\s*content: \"\\\\(....)", fa):
    name = match.group(1).replace('-', ' ').title().replace(' ','')
    css = match.group(1)
    code = match.group(2).upper()
    line =("\\expandafter\\def\\csname faicon@%s\\endcsname              " +\
    "{\\symbol{\"%s}}  \\def\\fa%s             " +\
    "{{\\FA\\csname faicon@%s\endcsname}}\n") % (css, code, name,css)
    
    # group hex values in sets of 16
    if code[3] == '0': line = '\n' + line

    out.write(line)
    
out.write("""
\endinput


%% end of file 'fontawesome.sty'.
""")
        
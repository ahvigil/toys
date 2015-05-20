"""
typicon latex .sty file generator to create LaTeX package files
based on the fontawesome latex package at
http://www.ctan.org/tex-archive/fonts/fontawesome
but support for typicon font by Stephen Hutchins
http://typicons.com/

useage: python tilatex.py [typicons.yml]
get the latest typicons yaml file from
https://raw.githubusercontent.com/stephenhutchings/typicons.font/master/config.yml

@author Arthur Vigil
@date 9/8/14
"""

import re, os.path, sys

TI_PATH = "typicons.yml"

# use existing package text to start out 
INTRO = """
%% start of file `typicons.sty'.
%% Copyright 2013 Xavier Danaux (xdanaux@gmail.com).
%
% This work may be distributed and/or modified under the
% conditions of the LaTeX Project Public License version 1.3c,
% available at http://www.latex-project.org/lppl/.


%-------------------------------------------------------------------------------
%                identification
%-------------------------------------------------------------------------------
\NeedsTeXFormat{LaTeX2e}
\ProvidesPackage{typicons}[2013/05/10 v3.1.1 font awesome icons]


%-------------------------------------------------------------------------------
%                requirements
%-------------------------------------------------------------------------------
\usepackage{fontspec}


%-------------------------------------------------------------------------------
%                implementation
%-------------------------------------------------------------------------------

% definition of \TI as a shortcut to load the Typicon font
\\newfontfamily{\TI}{Typicons}

% generic command to display an icon by its name
\\newcommand*{\\ticon}[1]{%
  {\TI\csname ticon@#1\endcsname}}

% icon-specific commands
"""

# use argv as path to the typicon stylesheet if present
if len(sys.argv) is 2:
    TI_PATH = sys.argv[1]

if not os.path.exists(TI_PATH):
    print "%s file could be found, needed to continue" % TI_PATH
    sys.exit(1)
    
out = open('typicons.sty','w')
out.write(INTRO)

with open(TI_PATH) as config:
    ti = config.read()
    
    for match in re.finditer("css: (.*)\s*code: '0x(.*)'", ti):
        name = match.group(1).replace('-', ' ').title().replace(' ','')
        css = match.group(1)
        code = match.group(2).upper()
        line =("\\expandafter\\def\\csname ticon@%s\\endcsname              " +\
        "{\\symbol{\"%s}}  \\def\\ti%s             " +\
        "{{\\TI\\csname ticon@%s\endcsname}}\n") % (css, code, name,css)
        
        # group hex values in sets of 16
        if code[3] == '0': line = '\n' + line

        out.write(line)
        
out.write("""
\endinput


%% end of file 'typicons.sty'.
""")
        

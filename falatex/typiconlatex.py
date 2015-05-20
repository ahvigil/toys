"""
typicon latex .sty file generator to create LaTeX package files
based on the fontawesome latex package at
http://www.ctan.org/tex-archive/fonts/fontawesome
but with support for typicon font by Stephen Hutchins
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
%% Copyright 2015 Arthur Vigil (arthur.h.vigil@gmail.com)
%% Based on 'fontawesome' package by Xavier Danaux
%% Copyright 2013 Xavier Danaux (xdanaux@gmail.com).
%
% This work may be distributed and/or modified under the
% conditions of the LaTeX Project Public License version 1.3c,
% available at http://www.latex-project.org/lppl/.


%-------------------------------------------------------------------------------
%                identification
%-------------------------------------------------------------------------------
\NeedsTeXFormat{LaTeX2e}
\ProvidesPackage{typicons}[2015/05/20  v2.0.3 typicon icons]


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

CONTENT = r"""
%% start of file `typicon.tex'.
%% Copyright 2015 Arthur Vigil (arthur.h.vigil@gmail.com).
%%
%% Modified from fontawesome package by Xavier Danaux
%% Copyright 2013 Xavier Danaux (xdanaux@gmail.com).
%
% This work may be distributed and/or modified under the
% conditions of the LaTeX Project Public License version 1.3c,
% available at http://www.latex-project.org/lppl/.

\documentclass{ltxdoc}
%\GetFileInfo{\jobname.sty}
\def\fileversion{2.0.4}
\def\filedate{May 20, 2015}
\usepackage{lmodern}
\usepackage[numbered]{hypdoc}
\usepackage{hologo}
\usepackage{hyperref, xcolor}
\definecolor{myblue}{rgb}{0.22,0.45,0.70}% light blue
\hypersetup{colorlinks=true, linkcolor=myblue, urlcolor=myblue, hyperindex}
\usepackage{longtable, booktabs}
\usepackage{tikz}
\usepackage{xparse, ifthen}
\usepackage{\jobname}
\EnableCrossrefs
\CodelineIndex
\RecordChanges

\begin{document}
\title{The \textsf{\jobname} package\\More high quality web icons}
\author{%
Arthur Vigil\thanks{E-mail: \href{mailto:arthur.h.vigil@gmail.com}{\tt arthur.h.vigil@gmail.com}} (\hologo{LaTeX} code)\\%
Xavier Danaux (more \hologo{LaTeX} code)\\%
Stephen Hutchings (font and icons design)}
\date{Version \fileversion, released on \filedate}
\maketitle

\begin{abstract}
The \textsf{\jobname} package grants access to 336 web-related icons provided by the included \emph{Typicon} free font, designed by Stephen Hutchings and released\footnote{See \url{http://www.typicons.com/} for more details about the font itself} under the open SIL Open Font License\footnote{Available at \url{http://scripts.sil.org/OFL}.}.

This package requires the \textsf{fontspec} package and either the \hologo{Xe}\hologo{(La)TeX} or Lua\hologo{(La)TeX} engine to load the included woff font.
\end{abstract}

\changes{v2.0.7}  {2015/05/20}{First public release (version number set to match the included typicons.woff font version).}
\makeatletter
\let\PrintMacroName@original\PrintMacroName
%\let\PrintDescribeMacro\@gobble
%\let\PrintDescribeEnv\@gobble
\let\PrintMacroName\@gobble
%\let\PrintEnvName\@gobble
\begin{macro}{\faTextHeight}
\changes{v3.0.2-1}{2013/03/23}{Corrected binding.}
\end{macro}
\begin{macro}{\faTextWidth}
\changes{v3.0.2-1}{2013/03/23}{Corrected binding.}
\end{macro}
\let\PrintMacroName\PrintMacroName@original
\makeatother

\bigskip

\section{Introduction}
The \textsf{\jobname} package aims to enable easy access in \hologo{(La)TeX} to high quality
\hyperref[section:icons]{icons}.
It is a redistribution of the free (as in beer) \emph{Typicons} woff font with specific bindings for \hologo{(La)TeX}, based on the similar \textsf{fontawesome} package.

\section{Requirements}
The \textsf{\jobname} package requires the \textsf{fontspec} package and either the \hologo{Xe}\hologo{(La)TeX} or Lua\hologo{(La)TeX} engine to load the included woff font.

\section{Usage}
\DescribeMacro{\ticon}
Once the \textsf{\jobname} package loaded, icons can be accessed through the general \cs{ticon}, which takes as mandatory argument the \meta{name} of the desired icon, or through a direct command specific to each icon. The full list of icon designs, names and direct commands are showcased next.

\newenvironment{showcase}%
{%
%   \begin{longtable}{ccp{3cm}p{3.5cm}p{1cm}}% debug: shows icons with both generic and specific commands
\begin{longtable}{cp{4cm}p{3.5cm}p{1cm}}
\cmidrule[\heavyrulewidth]{1-3}% \toprule
%   \bfseries Icon& \bfseries Icon& \bfseries Name& \bfseries Direct command& \\% debug
\bfseries Icon& \bfseries Name& \bfseries Direct command& \\
\cmidrule{1-3}\endhead}
{\cmidrule[\heavyrulewidth]{1-3}% \bottomrule
\end{longtable}}
\NewDocumentCommand{\showcaseicon}{mmg}{%
%  \ticon{#1}& \csname#2\endcsname& \itshape #1& \ttfamily \textbackslash #2\index{\ttfamily \textbackslash #2}& \IfNoValueTF{#3}{}{\tag{#3}}\\}% debug
\ticon{#1}& \itshape #1& \ttfamily \textbackslash #2\index{\ttfamily \textbackslash #2}& \IfNoValueTF{#3}{}{\tag{#3}}\\}
\newcommand{\tag}[1]{{%
\small\sffamily%
\ifthenelse{\equal{#1}{new}}{%
\tikz[baseline={(TAG.base)}]{
\node[white, fill=myblue, rounded corners=3pt, inner sep=1.5pt] (TAG) {new!\vphantom{Ay!}};
}}{}%
\ifthenelse{\equal{#1}{gone}}{%
\tikz[baseline={(TAG.base)}]{
\node[black!50, fill=black!25, rounded corners=3pt, inner sep=1.5pt] (TAG) {gone (?)\vphantom{Ay!}};
}}{}%
\ifthenelse{\equal{#1}{alias}}{%
\textcolor{black!50}{(alias)}}{}%
}}

\subsection{Typicon icons\label{section:icons}}
\begin{showcase}
"""

# use argv as path to the typicon stylesheet if present
if len(sys.argv) is 2:
  TI_PATH = sys.argv[1]

if not os.path.exists(TI_PATH):
  print "%s file could be found, needed to continue" % TI_PATH
  sys.exit(1)

out = open('typicons.sty','w')
doc = open('typicons.tex', 'w')
out.write(INTRO)
doc.write(CONTENT)

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
    
    line=("\t\\showcaseicon{%s}{ti%s}\n") % (css, name)
    doc.write(line)
    out.write(r"""
  \endinput
  
  
  %% end of file 'typicons.sty'.
  """)
out.close()
              
doc.write("""
            \end{showcase}

            \end{document}
            
            
            %% end of file `typicons.tex'.
    """)
doc.close()

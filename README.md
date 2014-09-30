##Fortgeschrittenenpraktikum (Teil 1)

####Useful links

- [information (2014)](http://portal.uni-freiburg.de/jakobs/Lehre/ss2014/fp2014-2)
- [information (general)](http://portal.uni-freiburg.de/jakobs/Fortgeschrittenen-Praktikum)
- [instructions](http://hacol13.physik.uni-freiburg.de/fp/)
- [list of tutors](http://hacol13.physik.uni-freiburg.de/fp/fp2014-2/Assistenten.pdf)

####Schedule

| Day      | Date | Description               | Δt/d |  
|----------|------|---------------------------|------|  
|Montag    | 08.09| Lange Halbwertszeiten     |  -   |  
|Dienstag  | 16.09| I2-Molekül                | 6.5  |  
|Freitag   | 19.09| Szintillationszähler       | 1.5  |  
|Mittwoch  | 24.09| Farady- und Pockelseffekt | 3.5  |  
|Donnerstag| 02.10| Halbleiter                | 6.5  |  
|Mittwoch  | 08.10| Ringlaser                 | 4.5  |  
|Montag    | 13.10| Kernspinresonanz          | 3.5  |  
|Donnerstag| 16.10| Hanle-Effekt              | 1.5  |  
|Dienstag  | 21.10| SQUID                     | 3.5  |  

####Setup
We use the latest [Eclipse](https://www.eclipse.org/) version as IDE with following plugins:
- [TeXlipse](http://texlipse.sourceforge.net/) for LaTeX
- [PyDev](http://pydev.org/) for Python

#####Running LaTeX scripts
You can import the existing project with Eclipse. You can check our configuration in the `.texlipse` file.

#####Running Python scripts
Unfortunatley we cant sync our `.pydevproject` configuration file, because PyDev saves absolute paths. You need to add the `lib` folder by yourself to the `PYTHONPATH` (for example add it to the `external libraries` list of the project).

####directory structure
Every experiment has its own directory. In this directory you may find following subdirectories:
- `bin`: binary file of protocol (not final version), excluded from commits
- `calc`: results of fits and raw data for further calculation
- `data`: measured data from experiment, also includes pictures made in the experiment
- `img`: rendered graphs from ROOT and self-made svg-graphics
- `src`: source dir for python and latex code
- `stuff`: mostly mathematica files for on-the-fly evaluation and error calculation

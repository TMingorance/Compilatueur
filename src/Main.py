import argparse
import logging
import sys

from src import analex, MV
from src.anasyn import program, tabId, tabInstr

logger = logging.getLogger('anasyn')

DEBUG = False
LOGGING_LEVEL = logging.DEBUG


########################################################################
def main():
    parser = argparse.ArgumentParser(description='Do the syntactical analysis of a NNP program.')
    parser.add_argument('inputfile', type=str, nargs=1, help='name of the input source file')
    parser.add_argument('-o', '--outputfile', dest='outputfile', action='store', default="",
                        help='name of the output file (default: stdout)')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.0')
    parser.add_argument('-d', '--debug', action='store_const', const=logging.DEBUG, default=logging.INFO,
                        help='show debugging info on output')
    parser.add_argument('-p', '--pseudo-code', action='store_const', const=True, default=False,
                        help='enables output of pseudo-code instead of assembly code')
    parser.add_argument('--show-ident-table', action='store_true', help='shows the final identifiers table')
    args = parser.parse_args()

    filename = args.inputfile[0]
    f = None
    try:
        f = open(filename, 'r')
    except FileNotFoundError:
        logger.error("Error: can\'t open input file!")
        return

    outputFilename = args.outputfile

    # create logger
    LOGGING_LEVEL = args.debug
    logger.setLevel(LOGGING_LEVEL)
    ch = logging.StreamHandler()
    ch.setLevel(LOGGING_LEVEL)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    #if args.pseudo_code:
    #    True  #
    #else:
     #   False  #

    lexical_analyser = analex.LexicalAnalyser()

    lineIndex = 0
    for line in f:
        line = line.rstrip('\r\n')
        lexical_analyser.analyse_line(lineIndex, line)
        lineIndex = lineIndex + 1
    f.close()

    # launch the analysis of the program
    lexical_analyser.init_analyser()
    program(lexical_analyser)

    if args.show_ident_table:
        print("------ IDENTIFIER TABLE ------")
        print(str(tabId))
        print("------ END OF IDENTIFIER TABLE ------")

    if outputFilename != "":
        try:
            output_file = open(outputFilename, 'w')
        except:
            print("Error: can\'t open output file!")
            return
    else:
        output_file = sys.stdout

    # Outputs the generated code to a file
    # instrIndex = 0
    # while instrIndex < codeGenerator.get_instruction_counter():
    #        output_file.write("%s\n" % str(codeGenerator.get_instruction_at_index(instrIndex)))
    #        instrIndex += 1

    if outputFilename != "":
        output_file.close()

    lexical_analyser.save_to_file("")

    for lexicalUnit in lexical_analyser.lexical_units:
        logger.debug(str(lexicalUnit))

    for i in range(len(tabInstr)):
        logger.debug(str(i) + ' : ' + tabInstr[i])

    # Execution de la machine virtuelle
    mv = MV.MachineVirtuelle()
    mv.mVExecution(tabInstr)


########################################################################

if __name__ == "__main__":
    main()

from os.path import dirname
from django.conf import settings
from pipeline.compilers import SubProcessCompiler


class PySCSSCompiler(SubProcessCompiler):
    output_extension = 'css'

    def match_file(self, filename):
        return filename.endswith('.scss')

    def compile_file(self, infile, outfile, outdated=False, force=False):
        command = "%s %s < %s > %s" % (
            settings.PIPELINE_PYSCSS_BINARY,
            settings.PIPELINE_PYSCSS_ARGUMENTS,
            infile,
            outfile
        )
        return self.execute_command(command, cwd=dirname(infile))

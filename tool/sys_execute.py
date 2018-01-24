import subprocess
import tool.logger as logger


def execute(command):
    try:
        logger.g_logger.debug("subprocess = " + str(command))
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output, error = process.communicate()
        if process.returncode:
            logger.g_logger.error("error[{:d}]: \n{:s}".format(process.returncode, error))
            return (process.returncode, None)
        logger.g_logger.debug("\n" + output + error)
        return (0, output)
    except Exception as e:
        logger.g_logger.error("Exception = `%s`" % str(e));
        raise e

    return (1, None)
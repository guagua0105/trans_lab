# -*- coding: UTF-8 -*-
import transQulity
import tool.logger as logger
import src.define.input as inputStruct
import src.define.output as outputStruct


class BatchTransQulity:
    def setParams(self, baseVideoBitrate, baseMediaParams, baseInputArray, showSize):
        self.baseVideoBitrate = baseVideoBitrate
        self.baseMediaParams = baseMediaParams
        self.baseInputArray = baseInputArray
        self.showSize = showSize


    def transAndQulity(self):
        BaseOutputArray = outputStruct.BaseOutputArray()
        for i in range(0, len(self.baseInputArray)):
            input = self.baseInputArray.__getitem__(i)
            transQulityObj = transQulity.TransQulity()

            transQulityObj.setParams(self.baseVideoBitrate, self.baseMediaParams, input, self.showSize)

            (res, output) = transQulityObj.transAndQulity()
            if res < 0:
                logger.g_logger.error("get transQulityObj.transAndQulity() error")

            BaseOutputArray.append(output)

        return BaseOutputArray


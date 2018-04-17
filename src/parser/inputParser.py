import src.define.input as inputStruct
import json

class InputParser:
    def Parser(self,jsonPath):
        with open(jsonPath, 'r') as json_file:
            inputs = json.load(json_file)

        if json_file == None:
            return (-1, None)

        BaseInputArray = inputStruct.BaseInputArray()

        for i in range(0, len(inputs)):
            input = inputStruct.BaseInput()
            input.input_path = inputs[str(i)]["input_path"]
            input.input_trans_path = inputs[str(i)]["trans_file_path"]
            input.vmaf_result_path = inputs[str(i)]["vmaf_result_path"]
            BaseInputArray.append(input)


        return (1, BaseInputArray)
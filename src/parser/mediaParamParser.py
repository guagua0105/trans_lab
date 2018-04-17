import src.define.mediaParams
import json

class MediaParamParser:
    def Parser(self,jsonPath):
        with open(jsonPath, 'r') as json_file:
            jsonStruct = json.load(json_file)

        if json_file == None:
            return (-1, None, None)

        baseMediaParamsArray = src.define.mediaParams.baseMediaParamsArray()
        subJsonStruct = jsonStruct["baseMediaParams"]
        for i in range(0, subJsonStruct):
            baseMediaParams = src.define.mediaParams.baseMediaParams()
            baseMediaParams.stream_select = jsonStruct[i]["stream_select"]
            baseMediaParams.vencoder_params = jsonStruct[i]["vencoder_params"]
            baseMediaParams.vfilter_params = jsonStruct[i]["vfilter_params"]
            baseMediaParams.format_params = jsonStruct[i]["format_params"]
            baseMediaParams.aencoder_params = jsonStruct[i]["aencoder_params"]
            baseMediaParamsArray.append(baseMediaParams)

        baseVideoBitrateArray = src.define.mediaParams.baseVideoBitrateArray()
        subJsonStruct = jsonStruct["baseVideoBitrates"]
        for i in range(0, subJsonStruct):
            baseVideoBitrate = src.define.mediaParams.baseVideoBitrate()
            baseVideoBitrate.rc_mode = subJsonStruct[i]["rc_mode"]
            baseVideoBitrate.output_bitrate = subJsonStruct[i]["output_bitrate"]
            baseVideoBitrate.crf = subJsonStruct[i]["crf"]
            baseVideoBitrateArray.append(baseVideoBitrate)


        return (1, baseMediaParams, baseVideoBitrateArray)
# trans_lab
该工程包括三部分：
1、视频信息查询：
	可以指定查询条件、键值从ELK中查询信息；
2、视频下载：
	根据输入objectid查询下载地址、防盗处理最后下载该视频；
3、转码质量评价：
	针对视频进行转码，将转码后视频与源视频同时解码成YUV，使用vmaf、psnr等工具进行评分；


当前工具已经上传到GitHub，使用前环境配置：
1、下载视频压缩实验工具，URL：https://github.com/guagua0105/trans_lab；
2、安装VMAF工具，URL：https://github.com/Netflix/vmaf；
3、下载或者在本地编译FFmpeg，URL：https://www.ffmpeg.org/download.html;
4、设置运行环境：config/run_config.py，分别为本地的工具路径;
5、设置ELK、防盗链以及对象库请求地址：config/run_config.py；
7、设置ELK查询条件：config_query_config.py；


使用案例：
1、下载TOP100的视频：
	src/network/test_top_video_downloader.py -n 100 -j -V output_dir -f
	-V output_dir为输出路径，并且形成json；

2、统计某个转码方法对于TOP100的压缩质量：
	src/worker/quality_lab_from_json.py -i inputinfo.json -o result.json
	-i inputinfo.json ，为输入信息描述，暂时需要手动生成；
	-o result.json，为最终输出得分信息；
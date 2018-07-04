# -*- coding: UTF-8 -*-
import os, sys
import urllib2
import json
import config.url_config as url_config
import tool.logger as logger



class VideoDownloader():

    def checkoutput(self, output, b_overwrite):
        if os.path.isfile(output):
            if not b_overwrite:
                logger.g_logger.warning(output + " already exist")
                return 1
            else:
                logger.g_logger.warning(output + " would be overwrite")
        return 0

    def get_ssig_url(self, input_url):
        # 获取 ssig
        try:
            get_ssig_api = url_config.ssig_api_str % (url_config.appkey, input_url)
            logger.g_logger.info("get_ssig_api = " + get_ssig_api)
            req = urllib2.urlopen(get_ssig_api)
            ret_json = req.read()
            ret_dict = json.loads(ret_json)
            ssig_url = ret_dict['result_data']['ssig_url']
            logger.g_logger.debug("get_ssig_api ret: %s" + ret_json)
            logger.g_logger.info("ssig_url = " + ssig_url)
        except Exception as e:
            logger.g_logger.error("Exception e = %s", e);
            return None
        return ssig_url

    def get_ssig_url_with_original(self, object_id):
        # 获取原始视频
        try:
            get_source_api = url_config.source_api_str % (url_config.appkey, url_config.url_ssig, object_id)
            logger.g_logger.info("get_source_api = " + get_source_api)
            req = urllib2.urlopen(get_source_api)
            ret_json = req.read()
            logger.g_logger.debug("get_source_api ret: %s" + ret_json)
            ret_dict = json.loads(ret_json)
            #with open(path_prefix + ".json", "wb") as f:
                #json.dump(ret_dict, f, indent=4)
        except Exception as e:
            logger.g_logger.error("Exception e = %s", e);
            return None

        url = ret_dict['object']['original_url']

        if url == None:
            logger.g_logger.warning("no url for label " + label)
        ssig_url = self.get_ssig_url(url)
        if not ssig_url:
            logger.g_logger.error("get ssig url for '%s' failed", url)
            return (-2,None)
        return ssig_url

    def get_ssig_url_with_mp4_hd(self, object_id):
        # 获取原始视频
        try:
            get_source_api = url_config.source_api_str % (url_config.appkey, url_config.url_ssig, object_id)
            logger.g_logger.info("get_source_api = " + get_source_api)
            req = urllib2.urlopen(get_source_api)
            ret_json = req.read()
            logger.g_logger.debug("get_source_api ret: %s" + ret_json)
            ret_dict = json.loads(ret_json)
            #with open(path_prefix + ".json", "wb") as f:
                #json.dump(ret_dict, f, indent=4)
        except Exception as e:
            logger.g_logger.error("Exception e = %s", e);
            return None

        url = ret_dict['object']['urls']['mp4_hd_mp4']


        return url


    def videoDownload(self, object_id, odir=None, opath=None, b_overwrite=False):
        # 设置存储文件名
        name = object_id.replace(":", "_")
        odir = odir if odir else os.getcwd()
        path_prefix = os.path.join(odir, name)

        # 获取原始视频
        label = "mp4_hd_mp4"
        ssig_url = self.get_ssig_url_with_mp4_hd(object_id)
        if not ssig_url:
            return (-2,None)

        opath = path_prefix + "." + label + ".mp4"
        logger.g_logger.info("save_path = " + opath)

        # 下载视频
        if not self.checkoutput(opath, b_overwrite):
            try:
                link = urllib2.urlopen(ssig_url)
                with open(opath, 'wb') as f:
                    f.write(link.read())
                link.close()
                logger.g_logger.info("download finished")
            except Exception as e:
                logger.g_logger.error("Exception e = %s", e);
                return (-3,None)
        return (0,opath)

    def videoDownloadWithUrl(self, video_url, odir=None, name=None, b_overwrite=False):
        ssig_url = self.get_ssig_url(video_url)
        if not ssig_url:
            return (-2,None)

        opath = odir + "/" + name + ".mp4"
        logger.g_logger.info("save_path = " + opath)

        # 下载视频
        if not self.checkoutput(opath, b_overwrite):
            try:
                link = urllib2.urlopen(ssig_url)
                with open(opath, 'wb') as f:
                    f.write(link.read())
                link.close()
                logger.g_logger.info("download finished")
            except Exception as e:
                logger.g_logger.error("Exception e = %s", e);
                return (-3,None)
        return (0,opath)
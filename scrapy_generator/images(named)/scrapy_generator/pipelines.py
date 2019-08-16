# -*- coding: utf-8 -*-
from scrapy.pipelines.images import ImagesPipeline

class Scrapy_generatorPipeline(ImagesPipeline):
	#Name download version
    def file_path(self, request, response=None, info=None):
        image_guid = request.url.split('/')[-1]
        return 'full/%s' % (image_guid)

    #Name thumbnail version
    def thumb_path(self, request, thumb_id, response=None, info=None):
        image_guid = thumb_id + request.url.split('/')[-1]
        return 'thumbs/%s/%s.jpg' % (thumb_id, image_guid)

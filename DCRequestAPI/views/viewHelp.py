import logging
log = logging.getLogger(__name__)

from pyramid.response import Response
from pyramid.renderers import render_to_response
from pyramid.view import (view_config, view_defaults)
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPSeeOther

import pudb
import json



class helpView():
	def __init__(self, request):
		self.request = request
		pass
	
	
	@view_config(route_name='help', accept='text/html', renderer="DCRequestAPI:templates/help.pt")
	def helpPage(self):
		pagecontent = {
			'pagetitle': 'API for requests on DiversityCollection database',
			'applicationurl': self.request.application_url
			
		}
		return pagecontent

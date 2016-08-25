# -*- coding: utf-8 -*-
import http.client, urllib, ssl, socket, urllib.request;

class Connection:
	myconn = None;
	myurl = None;
	myssl = True;
	
	mycookies = {};
	
	redirect = None;	
	
	def __init__(self, url):
		self.myurl = url;
		self.redirect = None;
	
	def urlencode(self, arg):
		return urllib.parse.urlencode(arg);
		
	
	def refreshConn(self):
		if(self.myssl == True):
			self.myconn = http.client.HTTPSConnection(self.myurl);
		else:
			self.myconn = http.client.HTTPConnection(self.myurl);
		return True;

	
	def setSecure(self, isSecure):
		self.myssl = isSecure;
		
		
	def refreshCookies(self, response):
		setcookie = response.getheader("Set-Cookie", None);
		if(setcookie == None):
			return;
			
		_cookie_start = True;
		_cookie_parametervalue = "";
		_cookie_parameter = "";
		_cookie_name = "";
		_cookie_value = "";
		_cookie_invalue = False;
			
		for i in range(0, len(setcookie)):
			if(setcookie[i] == ';'):
				if(_cookie_start == True):
					self.mycookies[_cookie_name] = _cookie_value;
				
				_cookie_start = False;
				_cookie_parameter = "";
				_cookie_parametervalue = "";
				_cookie_invalue = False;
			elif(setcookie[i] == ',' and _cookie_parameter != "expires"):
				_cookie_start = True;
				_cookie_name = "";
				_cookie_parameter = "";
				_cookie_parametervalue = "";
				_cookie_value = "";
				_cookie_invalue = False;
			elif(setcookie[i] == '='):
				_cookie_invalue = True;
				if(_cookie_start == True):
					_cookie_name = _cookie_name.strip();
				else:
					_cookie_parameter = _cookie_parameter.strip();
			else:
				if(_cookie_invalue == False):
					if(_cookie_start == True):
						_cookie_name += setcookie[i];
					else:
						_cookie_parameter += setcookie[i];
				else:
					if(_cookie_start == True):
						_cookie_value += setcookie[i];
					else:
						_cookie_parametervalue += setcookie[i];
				
				
	def getCookies(self):
		retStr = "";
		for cookie in self.mycookies.keys():
			if(len(retStr) > 0):
				retStr += "; ";
			retStr += str(cookie)+"="+str(self.mycookies[cookie]);
		return retStr;
		
	
	def get(self, url):
		#if(self.refreshConn() == False):
			#return None;
			
		headers = {"X-Requested-With": "XMLHttpRequest",
							 "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.66 Safari/537.36"};
		if(len(self.mycookies) > 0):
			headers['Cookie'] = self.getCookies();
			
		#try:			
		#print("HI");
		fUrl = ("http://" if not self.myssl else "https://")+self.myurl+"/"+url;
		#print(fUrl);
		response = urllib.request.urlopen(urllib.request.Request(fUrl, None, headers));
		#self.myconn.request("GET", url, None, headers);
		#response = self.myconn.getresponse();
		#except (http.client.BadStatusLine, ssl.SSLError, socket.gaierror, socket.error):
		#	response = None;
			
		if(response == None):
			return None;
			
		#print("[errorStatus: %s %03d %s]" % (url, response.status, response.reason));
		
		if(response.status != 200 and response.status != 302 and response.status != 401):
			return None;
			
		if response.status != 302:
			self.redirect = None;
		else:
			self.redirect = response.getheader("Location");
			
		response_data = response.read();
		
		self.refreshCookies(response);
		
		return response_data;
		
		
	def post(self, url, parameters):
		if(self.refreshConn() == False):
			return None;
			
		headers = {"Content-Type": "application/x-www-form-urlencoded",
							 "X-Requested-With": "XMLHttpRequest",
							 "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.66 Safari/537.36"};
		if(len(self.mycookies) > 0):
			headers['Cookie'] = self.getCookies();
			
		#print "POST %s %s" % (repr(url), repr(parameters));
		
		try:
			self.myconn.request("POST", url, self.urlencode(parameters), headers);
			response = self.myconn.getresponse();
		except (http.client.BadStatusLine, ssl.SSLError, socket.gaierror, socket.error):
			response = None;
		
		if(response == None):
			return None;
		
		#print("[errorStatus: %s %03d %s]" % (url, response.status, response.reason));
		
		if(response.status != 200 and response.status != 302 and response.status != 401):
			print("[errorStatus: %s %03d %s]" % (url, response.status, response.reason));
			#print(response.read());
			return None;
			
		if response.status != 302:
			self.redirect = None;
		else:
			self.redirect = response.getheader("Location");
			
		response_data = response.read();
		
		self.refreshCookies(response);
		
		return response_data;
		

	def close(self):
		self.myconn.close();
		
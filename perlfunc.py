#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

'''
/*  Copyright 2007, Jose Rodriguez (a.k.a. Boriel), http://www.boriel.com
**
**  This program is free software; you can redistribute it and/or modify
**  it under the terms of the GNU General Public License as published by
**  the Free Software Foundation; either version 2 of the License, or
**  (at your option) any later version.
**
**  This program is distributed in the hope that it will be useful,
**  but WITHOUT ANY WARRANTY; without even the implied warranty of
**  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
**  GNU General Public License for more details.
**
**  You can read it at: http://www.gnu.org/copyleft/gpl.html or
**  write to the Free Software Foundation, Inc., 59 Temple Place,
**  Suite 330, Boston, MA  02111-1307  USA
*/
'''

import tempfile, os
from subprocess import Popen, PIPE
from types import *

# Dictionary containing PERL5LIB path for each function
__PERL5LIB = {}

# Default PERL include PATH
__DEFAULT_PERL5LIB = '.'

# Executes system command and captures output
def sys_exec(cmd, shell = True, env = None):
	if env is None:
		env = os.environ
	
	a = Popen(cmd, shell = shell, stdout = PIPE, stderr = PIPE, env = env)
	a.wait()	# Wait process to terminate
	if a.returncode: # Not 0 => Error
		raise IOError(a.communicate()[1])

	return a.communicate()[0]


# Perl path
PERL = sys_exec('which perl').strip(' \t\n\r')

# Set to True to leave the tmp file (for debug)
DEBUG = False

def perlargs(*args):
	def perl_elem(x):
		if x is None:
			return 'undef'

		t = type(x)
		if t == StringType or t == UnicodeType:
			return "'%s'" % str(x).replace("'", "\\'")

		return str(x)


	def perl_vector(vec):
		sep = result = ''
		for i in vec:
			t = type(i)
			result += sep
			if t == ListType:
				result += '[' + perl_vector(i) + ']'
			elif t == DictType:
				result += '{' + perl_dict(i) + '}'
			else:
				result += perl_elem(i)
			sep = ', '

		return result


	def perl_dict(vec):
		sep = result = ''
		for i in vec.keys():
			t = type(vec[i])
			result += sep + str(i) + ' => '
			if t == ListType:
				result += '[' + perl_vector(i) + ']'
			elif t == DictType:
				result += '{' + perl_dict(i) + '}'
			else:
				result += perl_elem(i)
			sep = ', '

		return result

	sep = ''
	result = '('
	for i in args:
		t = type(i)
		result += sep
		if t == DictType:
			result += '(' + perl_dict(i) + ')'
		elif t == ListType:
			result += '(' + perl_vector(i) + ')'
		else:
			result += perl_elem(i)
		sep = ', '

	result += ')'

	return result



# Decorator which allows to call a perl function from python
def perlfunc(fn):
	def new(*args):
		# 
		tmppipe, pipename = tempfile.mkstemp('.pipe', 'tmp_', '.', True)
		os.close(tmppipe)

		tmpfile, tmpname = tempfile.mkstemp('.pl', 'tmp_', '.', True)
		os.write(tmpfile, fn.func_doc)  # Writes the perl code
		os.write(tmpfile, r'''
		{
			my @rst;
			my $len;
			my $i;

			open(DAT, ">''' + pipename + '''") || die("Cannot Open File for communication");
	
			@rst = (%s%s);
			if (@rst) {
				$len = @rst;
			} else {
				$len = 0;
				print DAT 'None';
			}
	
			if ($len > 1) {
				print DAT '[';
			}
	
			for ($i = 0; $i < $len; $i++) {
				if ($i) {
					print DAT ', ';
				}
	
				$rst[$i] =~ s/\'/\\\'/g;
				print DAT "'" . $rst[$i] . "'";
			}
	
			if ($len > 1) {
				print DAT ']';
			}

			close(DAT);
		}

		''' % (fn.func_name, perlargs(*args)))
		os.close(tmpfile)

		try:
			env = os.environ							# Get OS environment vars
			env['PERL5LIB'] = __PERL5LIB[fn.func_name]  # Adds our PERL5LIB if defined
		except KeyError:
			env = os.environ
			env['PERL5LIB'] = __DEFAULT_PERL5LIB

		# Eval perl code
		result_stdout = sys_exec([PERL] + [tmpname], False, env = env)
		print '[perl]\t', result_stdout
		pipe = open(pipename, 'r')
		result_str = pipe.read()
		pipe.close()

		try:
			result = eval(result_str)
		except:
			result = result_str


		# Erases tmp file
		if not DEBUG:
			os.unlink(tmpname)
			os.unlink(pipename)

		return result

	return new # Decorated function 


# Decorator which adds perl includes
def perlreq(*modules):
	def require_inc(fn):
		def new(*args):
			return fn(*args)

		new.func_name = fn.func_name
		new.func_doc = fn.func_doc
		if new.func_doc is None:
			new.func_doc = ''

		for i in modules:
			new.func_doc = 'require(\'%s\');\n' % i + new.func_doc
		return new

	return require_inc

	
# Decorator which changes perl includepath
def perl5lib(*paths):
	def include_fun(fn):
		global __PERL5LIB

		def new(*args):
			return fn(*args)

		new.func_name = fn.func_name
		new.func_doc = fn.func_doc

		try:
			PATH = __PERL5LIB[fn.func_name] + ':'
		except KeyError: # Not defined in __PERL5LIB yet
			PATH = ''

		__PERL5LIB[fn.func_name] = PATH + ':'.join(paths)
		return new

	return include_fun	



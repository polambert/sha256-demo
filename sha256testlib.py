
import math

## Define functions

total_xors = 0
total_shrs = 0
total_majs = 0
total_chs = 0
total_adds = 0

log_totals = False

# Logging Functions
def PrintHeader(title):
	print()
	print("----" + "-" * len(title))
	print("- {} -".format(title))
	print("----" + "-" * len(title))

# Utility Functions
def FillLeadingZeroes(x, length):
	zeroes = length - len(x)
	return "0" * zeroes + x

def DecAsBinary(dec):
	# dec can be int or str
	return bin(int(dec))[2:]

def StringAsByteArray(string):
	a = []
	for c in string:
		a.append(ord(c))
	return a

def ByteArrayAsBinary(byte_array):
	r = ""
	for n in byte_array:
		r += FillLeadingZeroes(bin(n)[2:], 8)
	return r

def AsciiAsBinary(ascii):
	r = ""
	for c in ascii:
		r += FillLeadingZeroes(bin(ord(c))[2:], 8)
	return r

# Bitwise Functions
def SHR(x, amount=1):
	global total_shrs
	for i in range(amount):
		x = ("0" + x)[:-1]
	total_shrs += amount
	if log_totals:
		print("Total SHRs: {}".format(total_shrs))
	return x

def ROTR(x, amount=1):
	for i in range(amount):
		x = (x[-1] + x)[:-1]
	return x

def XOR(a, b):
	global total_xors
	# len of a and b should be the same
	if len(a) != len(b):
		print("ERROR: XOR input lengths cannot be unequal.")
		return "xor_error"
	# iterate over them
	res = ""
	for i in range(len(a)):
		ap = a[i]
		bp = b[i]
		# xor operation here
		x = "0" if ap == bp else "1"
		res += x
		total_xors += 1
		if log_totals:
			print("Total XORs: {}".format(total_xors))
	return res

def Add(a, b, modlength=32):
	global total_adds
	# step 1: add
	ai = int(a, 2)
	bi = int(b, 2)
	res = bin(ai + bi)[2:]
	# setp 2: modulus
	total_adds += 1
	if log_totals:
		print("Total Adds: {}".format(total_adds))
	return FillLeadingZeroes(res[-modlength:], 32)

def ChoiceOne(x, y, z):
	global total_chs
	total_chs += 1
	if log_totals:
		print("Total Chs: {}".format(total_chs))
	return (y if x == "1" else z)

def Ch(x, y, z):
	if len(x) != len(y) or len(y) != len(z):
		print("ERROR: Ch input lengths cannot be unequal.")
		return "ch_error"
	# iterate over them
	res = ""
	for i in range(len(x)):
		res += ChoiceOne(x[i], y[i], z[i])
	return res

def MajorityOne(x, y, z):
	global total_majs
	total_majs += 1
	if log_totals:
		print("Total Majs: {}".format(total_majs))
	return "0" if (x + y + z).count("0") >= 2 else "1"

def Maj(x, y, z):
	if len(x) != len(y) or len(y) != len(z):
		print("ERROR: Maj input lengths cannot be unequal.")
		return "maj_error"
	# iterate over them
	res = ""
	for i in range(len(x)):
		res += MajorityOne(x[i], y[i], z[i])
	return res

# Define complex functions

def Sigma0(x):
	# a = ROTR 7
	# b = ROTR 18
	# c = SHR 3
	# XOR a, b, c
	a = ROTR(x, 7)
	b = ROTR(x, 18)
	c = SHR(x, 3)
	return XOR(XOR(a, b), c)

def Sigma1(x):
	# a = ROTR 17
	# b = ROTR 19
	# c = SHR 10
	# XOR a, b, c
	a = ROTR(x, 17)
	b = ROTR(x, 19)
	c = SHR(x, 10)
	return XOR(XOR(a, b), c)

def UpSigma0(x):
	# a = ROTR 2
	# b = ROTR 13
	# c = ROTR 22
	# XOR a, b, c
	a = ROTR(x, 2)
	b = ROTR(x, 13)
	c = ROTR(x, 22)
	return XOR(XOR(a, b), c)

def UpSigma1(x):
	# a = ROTR 6
	# b = ROTR 11
	# c = ROTR 25
	# XOR a, b, c
	a = ROTR(x, 6)
	b = ROTR(x, 11)
	c = ROTR(x, 25)
	return XOR(XOR(a, b), c)

# Define compression functions

def T1(e, f, g, h, k, w):
	# T1 = usig1(e) + Ch(e, f, g) + h + k + w
	a = Add(UpSigma1(e), Ch(e, f, g))
	b = Add(h, Add(k, w))
	return Add(a, b)

def T2(a, b, c):
	# T2 = usig0(a) + Maj(a, b, c)
	i = UpSigma0(a)
	j = Maj(a, b, c)
	return Add(i, j)
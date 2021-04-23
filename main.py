
import math
import time
from sha256testlib import *

# https://www.youtube.com/watch?v=f9EbD6iY9zI

## 

log_compression = True
log_compression_in_place = True

# first 64 prime numbers
primes = [ 2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 
	37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 
	97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 
	149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 
	197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 
	257, 263, 269, 271, 277, 281, 283, 293, 307, 311 ]

def GetConstants():
	# returns 64 constants
	a = []
	for i in range(64):
		# cube root
		x = primes[i] ** (1/3)
		#print("{}x = {}".format(i, x))

		# keep multiplying by 16 and adding what we get
		x = x - math.floor(x)
		y = hex(math.floor(x * 2**32))[2:]
		#print("{}y = {}".format(i, y))

		# turn it into binary
		z = FillLeadingZeroes(bin(int(y, 16))[2:], 32)
		#print("{}z = {}".format(i, z))
		#print()

		a.append(z)
	return a

def GetStartingHashValues():
	h = []
	for i in range(8):
		a = math.sqrt(primes[i])
		b = (a - math.floor(a)) * 2**32
		c = bin(math.floor(b))[2:]
		d = FillLeadingZeroes(c, 32)
		h.append(d)
	return h


# main entry point

def main():
	## Message
	message_text = "abc"
	byte_array = StringAsByteArray(message_text)
	message = ByteArrayAsBinary(byte_array)

	# for later
	original_message_length = len(message)

	PrintHeader("Message")
	print("  input: {}".format(message_text))
	print("  bytes: {}".format(byte_array))
	print("  bin:   {} ({} bits)".format(message, len(message)))


	## Padding
	PrintHeader("Padding")
	print("  message: {} ({} bits)".format(message, len(message)))

	# Add a 1 bit at the end
	message += "1"
	print("  message: {} ({} bits)".format(message, len(message)))

	# Add zeroes until length is (a multiple of 512) - 64
	# leave 64 at the end for the length of the message
	target_length = math.ceil(len(message)/512)*512 - 64
	zeroes_to_add = target_length - len(message)
	message += "0" * zeroes_to_add
	print("  message: {} ({} bits)".format(message, len(message)))

	# length of message 
	message_length_in_binary = FillLeadingZeroes(DecAsBinary(original_message_length), 64)
	message += message_length_in_binary
	print("  message: {} ({} bits)".format(message, len(message)))


	## Constants
	constants = GetConstants()

	PrintHeader("Constants")
	for i in range(0, len(constants) // 2):
		print("  K{:<2} {}".format(i, constants[i]), end="")
		print("  K{:<2} {}".format(i+32, constants[i+32]))

	
	## Message Schedule
	PrintHeader("Message Schedule")

	w = []

	# for 1 block, message schedule ie 64 words.
	# our 512 bits only has 16 words, so we have to make them.
	
	# first 16 words come from message
	for i in range(0, len(message), 32):
		w.append(message[i:i+32])

	# create rest of words
	for t in range(16, 64):
		# = sig1(t-2) + (t-7) + sig0(t-15) + (t-16)
		a = Sigma1(w[t - 2])
		b = w[t - 7]
		c = Sigma0(w[t - 15])
		d = w[t - 16]
		res = Add(Add(a, b), Add(c, d))
		w.append(res)
	
	for i in range(0, len(w) // 2):
		print("  W{:<2} {}".format(i, w[i]), end="")
		print("  W{:<2} {}".format(i+32, w[i+32]))


	## Compression
	PrintHeader("Compression")

	# constants as k
	k = constants

	# working state registers h
	h = GetStartingHashValues()
	
	for i in range(len(h)):
		print("  H{:<2} {}".format(i, h[i]))

	lines = 18

	print("\n" * lines)

	for i in range(64):
		# go back
		if log_compression_in_place:
			print("\033[F" * (lines + 1))

		if log_compression:
			print("i = {}".format(i))
			print("-------")

			print("  W{:<2} {}".format(i, w[i]))
			print("  K{:<2} {}".format(i, k[i]))
			print()
		
		# a = T1 + T2
		# e = e + T1
		t1 = T1(h[4], h[5], h[6], h[7], k[i], w[i])
		t2 = T2(h[0], h[1], h[2])

		if log_compression:
			print("  T1  {}".format(t1))
			print("  T2  {}".format(t2))
			print()

		# move all of the words up (and discard H7)
		for j in range(7, 0, -1):
			h[j] = h[j-1]

		h[0] = Add(t1, t2)
		h[4] = Add(h[4], t1)

		if log_compression:
			for i in range(len(h)):
				print("  H{:<2} {}".format(i, h[i]))

		if log_compression:
			print("-------\n", flush=True)

		# time.sleep(-0.0015625 * (i-64))

	print("Add original values")
	print("---------------------")

	start_hash = GetStartingHashValues()

	for i in range(len(h)):
		print("  H{:<2} {}".format(i, h[i]), end="")
		print(" + {}".format(start_hash[i]))
		h[i] = Add(h[i], start_hash[i])

	print()
	for i in range(len(h)):
		print("  H{:<2} {}".format(i, h[i]))
	print("      ^ Final hash values\n")

	binary = "".join(h)
	decimal = int(binary, 2)
	hexa = hex(decimal)[2:]

	PrintHeader("Final hash values")

	print(" As binary:  {}".format(binary))
	print(" As decimal: {}".format(decimal))
	print(" As hex:     {}".format(hexa))

if __name__ == "__main__":
	main()
	#print(Add("1" + "0"*31, "1" + "0"*31))
	#print(UpSigma1("01010001000011100101001001111111"))
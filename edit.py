def similarityMetric(word1, word2):
	w1_c = [0]*256
	w2_c = [0]*256
	for i in word1:
		w1_c[ord(i)] += 1 
	for i in word2:
		w2_c[ord(i)] += 1

	matched_words = 0
	for i in xrange(256):
		matched_words += min(w1_c[i], w2_c[i])

	if (matched_words == 0):
		return 99999
	return (max(len(word1), len(word2)) / float(matched_words))


def editDistance(word1, word2):
	len_1=len(word1)

	len_2=len(word2)

	x =[[0]*(len_2+1) for _ in range(len_1+1)] # the matrix whose last element ->edit distance

	for i in range(0,len_1+1): # initialization of base case values

	    x[i][0]=i
	for j in range(0,len_2+1):

	    x[0][j]=j
	
	for i in range (1,len_1+1):


	    for j in range(1,len_2+1):

	        if word1[i-1]==word2[j-1]:
	            x[i][j] = x[i-1][j-1] 

	        else :
	            x[i][j]= min(x[i][j-1],x[i-1][j],x[i-1][j-1])+1

	return x[i][j]

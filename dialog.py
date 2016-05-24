import pymongo
import re
from edit import editDistance, similarityMetric


def myFind(product_name, property_name, productNameList, db):

	tag_cat_map = {"t": "tv", "m": "mobiles", "l": "laptops", "c": "cameras", "a": "ac", "f": "fridges"}
	brandList = ['apple', 'hp', 'lenovo', 'lg', 'micromax', 'samsung', 'sony', "nikon", "canon", "panasonic"]

	###############################
	# Mobile 		--> 'm'		  #
	# Televisions 	--> 't'       #
	# Laptops 		--> 'l' 	  #
	# Cameras 		--> 'c' 	  #
	# Fridges 		--> 'f' 	  #
	# ACs 	 		--> 'a' 	  #
	###############################

	f = open("properties.txt", 'r')
	propertyList = f.read().split('\n')
	propertyList = propertyList[:-1]

	product_name = product_name.strip(' ?!.')
	property_name = property_name.strip(' ?!.')
	product_terms = product_name.split(" ")

	min_score = 99999
	idx = -1
	count = 0
	for term in product_terms:
		for brand in brandList:
			score = editDistance(term, brand)
			if (score < min_score):
				idx = count
				min_score = score
				product_brand = brand
		count += 1

	product_terms[idx] = product_brand
	product_name = ' '.join(product_terms)

	temp_products = []
	temp_prop = []

	for product in productNameList:
		if (product[0] == product_brand):
			score = editDistance(product[0] + " " + product[1], product_name)
			metric2 = similarityMetric(product[0] + " " + product[1], product_name)
			final_metric = (score * metric2 * 2) / (score + metric2)
			temp_products.append((product[1], product[2], final_metric))

	temp_products.sort(key=lambda tup: tup[2]) 
	temp_products = temp_products[:10]

	for prop in propertyList:
		score = editDistance(prop, property_name)
		metric2 = similarityMetric(prop, property_name)
		final_metric = (score * metric2 * 2) / (score + metric2)
		temp_prop.append((prop, final_metric))

	temp_prop.sort(key=lambda tup: tup[1]) 
	temp_prop = temp_prop[0][0]

	outputs = []
	for product in temp_products:
		results = db[tag_cat_map[product[1]]].find({"_id": product[0]})[0]
		try:
			outputs.append((product_brand.capitalize() + " " + product[0].capitalize() + ": " + results[temp_prop].capitalize()).encode('utf-8'))
		except:
			pass
	return outputs


def findProduct(query):
	client = pymongo.MongoClient('mongodb://localhost:27017')
	db = client.dialog_system

	productNameList = []	

	categories = ["tv", "mobiles", "laptops", "cameras", "ac", "fridges"]

	for cat in categories:
		for product in db[cat].find():
			productNameList.append((product["brand"].encode('utf-8').lower(), product["model name"].encode('utf-8').lower(), cat[0].lower()))

	query = query.lower().split(',')
	query = [q.strip() for q in query]
	product_brand = ""

	stopwords_ptr = open("stop_words.txt", 'r')
	stop_words = stopwords_ptr.read().split('\n')
	stop_words = stop_words[:-1]

	if (len(query) < 2):
		query = query[0].split(" ")
		hashmap = [0]*len(query)
		idx = 0
		for term in query:
			if (term in stop_words):
				hashmap[idx] = 1
			idx += 1	

		first_stop = -1
		for i in xrange(len(query), 0, -1):
			if (hashmap[i-1] and first_stop == -1):
				product_name = query[i:]
				product_name = " ".join(product_name)
				first_stop = i-1
			elif (hashmap[i-1] and first_stop != -1):
				property_name = query[i:first_stop]
				property_name = " ".join(property_name)
				break
		return myFind(product_name, property_name, productNameList, db)
	elif (len(query) >= 2):
		if (len(query) == 2):
			if (len(query[1].split(" ")) > 2):
				# Comparision Query between two products
				products = []
				prod = []
				tmp = query[0].split(" ")
				for term in tmp:
					if (term not in stop_words):
						prod.append(term)

				products.append(" ".join(prod))
				prod = []

				tmp = query[1].split(" ")
				for term in tmp:
					if (term not in stop_words):
						prod.append(term)
				tmp = " ".join(prod)
				products.append(tmp.split("best")[0].strip())
				property_name = tmp.split("best")[1].strip()
				out = []
				for prod in products:
					results = myFind(prod, property_name, productNameList, db)
					val = results[0].split(":")[1].strip().replace(",", "")
					out.append({
						"name": results[0].split(":")[0].strip(),
						"prop": results[0].split(":")[1].strip(), 
						"val": re.findall("\d+\.*\d+", val)[0]
					})
				out.sort(key=lambda k: float(k['val']))
				if (property_name.strip(" ?.").lower() == "price"):
					a = []
					a.append(out[0]["name"] + ": " + out[0]["prop"])
					return a
				else:
					a = []
					a.append(out[-1]["name"] + ": " + out[-1]["prop"])
					return a
			else:		
				product_name = query[0]
				property_name = query[1]
				return myFind(product_name, property_name, productNameList, db)
		else:
			# Comparision Query for more than 2 products
			products = []

			for i in xrange(0, len(query)): 
				prod = []
				tmp = query[i].split(" ")
				for term in tmp:
					if (term not in stop_words):
						prod.append(term)
				if i != len(query) - 1:
					products.append(" ".join(prod))

			tmp = " ".join(prod)
			products.append(tmp.split("best")[0].strip())
			property_name = tmp.split("best")[1].strip()
			out = []
			for prod in products:
				results = myFind(prod, property_name, productNameList, db)
				val = results[0].split(":")[1].strip().replace(",", "")
				out.append({
					"name": results[0].split(":")[0].strip(),
					"prop": results[0].split(":")[1].strip(), 
					"val": re.findall("\d+\.*\d+", val)[0]
				})
			out.sort(key=lambda k: float(k['val']))
			if (property_name.strip(" ?.").lower() == "price"):
				a = []
				a.append(out[0]["name"] + ": " + out[0]["prop"])
				return a
			else:
				a = []
				a.append(out[-1]["name"] + ": " + out[-1]["prop"])
				return a
	else:
		return "QUERY SYNTAX ERROR, REQUIRED: [PRODUCT NAME], [PROPERTY]"

user_names = '^[a-z0-9A-Z_@.#+-]+$'
allowspace = '^[a-z0-9A-Z_@.#+! ]+$'
onlynumbers = '^[0-9]+$'
bitcoin = '^[123mn][a-km-zA-HJ-NP-Z1-9]{25,34}$'
btcamount = '^(?=.*?\d)\d*[.,]?\d*$'
general = "^[a-zA-Z0-9 _':><;.,!()+=`|,@$\#/?%*\s-]*$"
monero = '^[a-z0-9A-Z]*$'
amount = '^(?=.*?\d)\d*[.,]?\d*$'
onion = "^[A-Za-z0-9_-]*$"
subcommon_name = "^[a-zA-Z0-9_.-]*$"
bitcoinaddress = '^[123mn][a-km-zA-HJ-NP-Z1-9]{25,34}$'
url_regexp = '((?:https?://|s?ftps?://|file://|javascript:|data:|www\d{0,3}[.])[\w().=/;,#:@?&~*+!$%\'{}-]+)'
urllink = 'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._re\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)'
phonenumber = '^(\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}$'
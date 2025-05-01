export type Url = {
	short_url: string, 
	original_url: string, 
	url_type: string,
}

export type UrlResponse =  {
	user: string, 
	urls: Url[],
}
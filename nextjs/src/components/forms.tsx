'use client';

import { useState, Dispatch, SetStateAction, ChangeEvent } from "react";
import { UrlResponse } from "components/types/url_types"

/**
* Enter link and shorten link for desktop
*/
export function UrlSubmitForm(
{ 
	setUrlResp
} : {
	setUrlResp: Dispatch<SetStateAction<UrlResponse>>
}) {
	
	const [url, setUrl] = useState("");	

	function handleFileUpload(event: ChangeEvent<HTMLInputElement>) {				
		const file = event.target?.files?.[0] as File
		if(file === undefined){
			return
		}
		
		const body = new FormData()
		body.append('file', file )

		fetch(
			`${process.env.NEXT_PUBLIC_SERVER_HOST}/files/${file?.name}`, 
			{
				method: "POST",
				body: body,	
			}
		).then(res => res.json()).
		then(json => setUrlResp(json))
	}
	
	return (
		<form className="
			grid
			grid-cols-1
			grid-rows-4
			md:grid-cols-12
			md:grid-rows-[2fr_1fr_2fr]
			gap-6
			"
		>	
			<input 
				value={url}
				onChange={(event) => setUrl(event.target.value)}
				placeholder="Enter Link"
				type="url"
				required
				aria-label="Enter link to shorten"
				className="
				text-slate-100
				text-center
				py-3
				px-4
				
				border-4
				border-slate-600
				rounded-full
				
				md:col-span-6
				"
			/>
			
			<ShortenLink 
				url={url}
				setUrlResp={setUrlResp} 
			/>

			
			<div className="
				flex 
				items-center 
				justify-center 
				text-lg 
				text-gray-100 
				font-bold
				md:row-start-2
				md:col-span-full
				"
			>
				Or
			</div>
			
			<div className="
				relative 
				group
				md:row-start-3
				md:col-span-full
			">
				{/* Background blur halo */}
				<div className="
					absolute  
					bg-gradient-to-tr 
					from-blue-600/70 
					to-purple-600/70
					blur-sm  
					rounded-full 
					-inset-px
					group-hover:-inset-1 
					duration-300
					ease-in-out
					w-full
					">
				</div>
				
				<label 
					htmlFor="uploadFile1"
					className="
					relative
					flex
					items-center
					justify-center
					bg-slate-500 
					duration-300
					ease-in-out
					text-slate-100
					font-bold
						
					w-full
					h-full
					rounded-full
					cursor-pointer 
					
					"
				>
					<svg xmlns="http://www.w3.org/2000/svg" 
						viewBox="0 0 32 32"
						className="
						w-7 
						mr-2 
						fill-white 
						inline
						"
					>
						<path
							d="M23.75 11.044a7.99 7.99 0 0 0-15.5-.009A8 8 0 0 0 9 27h3a1 1 0 0 0 0-2H9a6 6 0 0 1-.035-12 1.038 1.038 0 0 0 1.1-.854 5.991 5.991 0 0 1 11.862 0A1.08 1.08 0 0 0 23 13a6 6 0 0 1 0 12h-3a1 1 0 0 0 0 2h3a8 8 0 0 0 .75-15.956z"
							data-original="#000000" 
						/>
						<path
							d="M20.293 19.707a1 1 0 0 0 1.414-1.414l-5-5a1 1 0 0 0-1.414 0l-5 5a1 1 0 0 0 1.414 1.414L15 16.414V29a1 1 0 0 0 2 0V16.414z"
							data-original="#000000" 
						/>
					</svg>
					Upload
					<input 
						onChange={handleFileUpload}
						type="file" 
						id='uploadFile1' 
						accept=".doc, .docx, .xml, image/svg+xml, application/pdf, text/plain, image/png, image/jpeg, application/vnd.openxmlformats-officedocument.wordprocessingml.document, application/vnd.oasis.opendocument.text"
						className="hidden" 
					/>
				</label>
			</div>
			
		</form>
	);
}


export function ShortenLink(
{
	url,
	setUrlResp,
}: {
	url: string,
	setUrlResp: Dispatch<SetStateAction<UrlResponse>>,
}) {
	
	function handleSubmitUrl() {
		
		const jsonBody = JSON.stringify(
			{ 
				original_url: url,
			}
		)
		
		fetch(
			`${process.env.NEXT_PUBLIC_SERVER_HOST}/urls`, 
			{
				method: "POST",
				body: jsonBody,
				headers: {
					"Content-Type": "application/json",
				},			
			}
		).then(res => res.json()).
		then(json => setUrlResp(json))
	}
	
	return (
		<div className="
			relative 
			group
			md:col-span-6
		">
			{/* Background blur halo */}
			<div className="
				absolute  
				bg-gradient-to-tr 
				from-blue-600/70 
				to-purple-600/70
				blur-sm  
				rounded-full 
				-inset-px
				group-hover:-inset-1 
				duration-300
				ease-in-out
				w-full
				">
			</div>
			<input
				onClick={handleSubmitUrl}
				type="button"
				value="Shorten Link"
				className="
				relative
				bg-blue-600
				text-slate-100
				font-bold
				
				py-3
				px-2
				rounded-full
				flex
				items-center
				justify-center
				cursor-pointer
				w-full
				"
			/>
		</div>		
	)	
}
import { UrlSubmitForm } from "components/forms"
import { Dispatch, SetStateAction } from "react"
import { UrlResponse } from "components/types/url_types"

export function Header(
{
	setUrlResp,
} : {
	setUrlResp: Dispatch<SetStateAction<UrlResponse>>
}){
	return (
		<div className="
			max-w-6xl
			mx-auto
			flex
			flex-col
			items-center
		">					
			<h1 className="
				text-4xl 
				md:text-6xl
				text-white
				font-extrabold
				pb-12
				pt-12
				text-center
			">
				<span className="
					bg-clip-text 
					bg-linear-to-tr 
					from-blue-600
					to-purple-600 
					text-transparent
					"
				>
					Shorten Long Links
				</span>
			</h1>
			<h2 className="
				md:text-xl
				text-lg
				pb-12
				text-center
				text-slate-100
			">
				Link shortening service with file upload capability
			</h2>

			<UrlSubmitForm 
				setUrlResp={setUrlResp}
			/>
		</div>
	)
}
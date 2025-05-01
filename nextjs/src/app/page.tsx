'use client'

import { useState } from "react"
import { UrlTable } from "components/table"
import { Header } from "components/header"
import { UrlResponse } from "components/types/url_types"

export default function Home() {
	const [urlResp, setUrlResp] = useState({} as UrlResponse);

    return (
		<div className="
			bg-gray-900
			h-full
			min-h-lvh
		">
			<Header 
				setUrlResp={setUrlResp}
			/>
			
			<div className="
				max-w-[60rem]
				mx-auto
				"
			>
				<UrlTable 
					urlResponse={urlResp}
				/>
					
			</div>
		</div>
    )
}

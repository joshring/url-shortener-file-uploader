'use client';

import { useState, useEffect } from "react";
import { UrlResponse, Url } from "components/types/url_types"


/**
 * Table for Urls retrieved from the API
 */
export function UrlTable(
{
	urlResponse,
} : {
	urlResponse: UrlResponse,
}) {
	
	const [urlList, setUrlList] = useState({} as UrlResponse);
	
	useEffect(() => {
		
		fetch(
			`${process.env.NEXT_PUBLIC_SERVER_HOST}/urls`, 
			{
				method: "GET",
				headers: {
					"Content-Type": "application/json",
				},
			}
		).then(res => res.json()).
		then(json => setUrlList(json as UrlResponse))
	
	}, [urlResponse])
	
	
	return (		
		<div className="
			py-20
		">
		<table className="
			text-gray-200
			w-full 
			text-sm 
			text-left 
			
		">
			<thead className=" 
				capitalize 
				bg-slate-700 
				text-gray-300
				
			">
				<tr>
					<th className="px-3 md:px-4 py-5">
						Short Link
					</th>
					<th className="px-3 md:px-4 py-5">
						Original Link
					</th>
					<th className="px-3 md:px-4 py-5">
						Link Type
					</th>
				</tr>
			</thead>
			<tbody>
				{urlList?.urls &&
				urlList.urls.map((urlItem: Url, index) => (
					<tr 
						key={index}
						className="
						border-b 
						border-slate-800"
					>
						<td className="px-3 md:px-4 py-4">
							<a href={urlItem.short_url}>{urlItem.short_url}</a>
						</td>
						<td className="px-3 md:px-4 py-4">
							<a href={urlItem.original_url}>{urlItem.original_url}</a>
						</td>
						<td className="px-3 md:px-4 py-4">
							{urlItem.url_type === "site_url" ? "Web Link" : "File Link"}	
						</td>
					</tr>
				))}
			</tbody>
		</table>
	</div>
)}
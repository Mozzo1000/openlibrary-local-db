import React, { useState, useEffect, useMemo } from "react";
import axios from "axios";
import { debounce } from 'lodash';
import { TextInput, Select, Label } from "flowbite-react";
import Skeleton from 'react-loading-skeleton'
import 'react-loading-skeleton/dist/skeleton.css'
import { RiSearch2Line, RiFilter3Line, RiSortAsc } from "react-icons/ri";
import languages from "./languages.json"; 
function App() {
    const [searchTerm, setSearchTerm] = useState('');
    const [suggestions, setSuggestions] = useState([]);
    const [loading, setLoading] = useState(false);
    const [showList, setShowList] = useState(false);
    const [searchNotFound, setSearchNotFound] = useState(false);
    const [limit, setLimit] = useState(10);
    const [lang, setLang] = useState('eng');
    const [sort, setSort] = useState('relevance');

    const loadingPlaceholder = [0, 1, 2, 3, 4, 5];

    const fetchSuggestions = (term, currentLimit, currentLang, currentSort) => {
        if (!term) return;
        
        setLoading(true);
        setSearchNotFound(false);

        axios.get(`${import.meta.env.VITE_API_URL}v1/search/${encodeURIComponent(term)}`, {
            params: {
                limit: currentLimit,
                lang: currentLang,
                sort: currentSort
            }
        }).then(
            response => {
                console.log(response.data)
                let newArray = response.data.map((item, i) => ({
                    id: i,
                    name: item.title,
                    isbn: item.isbn_13 || item.isbn_10 || (item.isbn ? item.isbn[0] : null),
                    author: item.author_names?.[0] || "Unknown Author"
                }));
                setSuggestions(newArray);
                setLoading(false);
                setShowList(true);
            },
            error => {
                if (error.response?.status === 404) {
                    setSuggestions([]);
                    setLoading(false);
                    setShowList(false);
                    setSearchNotFound(true);
                }
            }
        );
    };

    const debouncedFetch = useMemo(
        () => debounce((t, l, ln, s) => fetchSuggestions(t, l, ln, s), 400),
        []
    );

    useEffect(() => {
        if (searchTerm.trim() !== '') {
            debouncedFetch(searchTerm, limit, lang, sort);
        } else {
            setSuggestions([]);
            setShowList(false);
            setSearchNotFound(false);
        }
    }, [searchTerm, limit, lang, sort, debouncedFetch]);

    return (
        <div className="container mx-auto pt-10 w-full md:w-8/12 lg:w-6/12 px-4">
            <h1 className="text-xl font-bold pb-2">OpenLibrary Local Search</h1>
            <div className="flex flex-row gap-4 pb-4 text-sm">
                <a className="text-blue-600 hover:underline" href="https://github.com/Mozzo1000/openlibrary-local-db">Github</a>
                <a className="text-blue-600 hover:underline" href={import.meta.env.VITE_API_URL + "docs"}>API Docs</a>
            </div>

            <div className="flex flex-col gap-3 bg-gray-50 p-4 rounded-lg border border-gray-200">
                <TextInput 
                    icon={RiSearch2Line} 
                    id="search" 
                    type="text" 
                    placeholder="Search by book title or isbn..." 
                    onChange={(e) => setSearchTerm(e.target.value)} 
                    value={searchTerm} 
                />

                <div className="flex flex-wrap gap-4 items-center text-sm">
                    <div className="flex items-center gap-2">
                        <RiFilter3Line className="text-gray-400" />
                        <Select sizing="sm" value={lang} onChange={(e) => setLang(e.target.value)}>
                            {languages.map((l) => (
                                <option key={l.code} value={l.code}>
                                    {l.name}
                                </option>
                            ))}
                        </Select>
                    </div>

                    <div className="flex items-center gap-2">
                        <RiSortAsc className="text-gray-400" />
                        <Select sizing="sm" value={sort} onChange={(e) => setSort(e.target.value)}>
                            <option value="relevance">Relevance</option>
                            <option value="newest">Newest</option>
                            <option value="oldest">Oldest</option>
                        </Select>
                    </div>

                    <div className="flex items-center gap-2">
                        <Label htmlFor="limit" value="Limit:" className="text-xs text-gray-500" />
                        <Select sizing="sm" id="limit" value={limit} onChange={(e) => setLimit(e.target.value)}>
                            <option value={10}>10</option>
                            <option value={25}>25</option>
                            <option value={50}>50</option>
                        </Select>
                    </div>
                </div>
            </div>

            <p className="format pt-2 ml-2 text-xs text-gray-500">
                Search powered by <a href="https://openlibrary.org" className="underline" target="_blank" rel="noreferrer">OpenLibrary</a>
            </p>

            {searchNotFound && <p className="pt-4 ml-2 text-red-500 font-medium">No results found.</p>}

            <div className={`${showList ? "block" : "hidden"} mt-4 relative z-10 bg-white rounded-lg shadow-sm border border-gray-100 overflow-hidden`}>
                {loading ? (
                    loadingPlaceholder.map((_, i) => (
                        <div key={i} className="p-4 border-b last:border-0">
                            <div className="flex gap-4">
                                <Skeleton height={96} width={64} />
                                <div className="flex-1">
                                    <Skeleton count={2} />
                                </div>
                            </div>
                        </div>
                    ))
                ) : (
                    suggestions.map((data) => (
                        <div key={data.id} className="p-4 border-b last:border-0 hover:bg-gray-50 transition-colors">
                            <div className="flex gap-4 items-center">
                                <div className="flex-shrink-0">
                                    <img 
                                        className="object-contain h-24 w-16 bg-gray-100 rounded shadow-sm" 
                                        src={data.isbn ? `https://covers.openlibrary.org/b/isbn/${data.isbn}-M.jpg` : 'https://openlibrary.org/images/icons/avatar_book-sm.png'} 
                                        alt={data.name}
                                        onError={(e) => { e.target.src = 'https://openlibrary.org/images/icons/avatar_book-sm.png' }}
                                    />
                                </div>
                                <div className="flex-1">
                                    <a href={`https://openlibrary.org/isbn/${data.isbn}`} target="_blank" rel="noreferrer" className="group">
                                        <p className="font-semibold text-blue-700 group-hover:underline">{data.name}</p>
                                        <p className="text-sm text-gray-700 font-medium">by {data.author}</p>
                                        <p className="text-sm text-gray-500">ISBN: {data.isbn || "N/A"}</p>
                                    </a>
                                </div>
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
}

export default App;
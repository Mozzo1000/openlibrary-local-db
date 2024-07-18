import React, { useState, useEffect, useMemo } from "react";
import axios from "axios";
import { debounce } from 'lodash';
import { TextInput } from "flowbite-react";
import Skeleton from 'react-loading-skeleton'
import 'react-loading-skeleton/dist/skeleton.css'
import { RiSearch2Line } from "react-icons/ri";

function App() {
    const [searchTerm, setSearchTerm] = useState('');
    const [suggestions, setSuggestions] = useState([{id: 0, name: ""}]);
    const [loading, setLoading] = useState(false);
    const [showList, setShowList] = useState(false);
    const loadingPlaceholder = [0,1,2,3,4,5]
    const [searchNotFound, setSearchNotFound] = useState(false);

    const fetchSuggestions = (searchTerm) => {
      if (searchTerm) {
          axios.get(`http://localhost:5000/v1/search/${encodeURIComponent(searchTerm)}`).then(
            response => {
            let newArray = []
            for (let i = 0; i < response.data.length; i++) {
                console.log(response.data[i].isbn)
                newArray.push({id: i, name: response.data[i].title, isbn: response.data[i].isbn})
            }
            setSuggestions(newArray); // Assuming the API returns an array of suggestions*/
            setLoading(false);
            setShowList(true);

            },
            error => {
                console.error('Error fetching suggestions:', error);
                console.log(error.response.status)
                if (error.response.status === 404) {
                  console.log("NOT FOUND")
                  setLoading(false);
                  setShowList(false);
                  setSearchNotFound(true);
                }
            }
        )
        }
    };

    useEffect(() => {
        if (searchTerm.trim() === '') {
            setSuggestions([]);
            setLoading(false);
            setShowList(false);
            setSearchNotFound(false);
        } 
    }, [searchTerm]);

    const changeHandler = (e) => {
        if (e.target.value) {
            setLoading(true);
            setShowList(true);
            fetchSuggestions(e.target.value)
        }
    }

    const debouncedChangeHandler = useMemo(
        () => debounce(changeHandler, 400)
    ,[]);
    return (
      <div className="container mx-auto pt-10 w-6/12">
          <h1 className="text-lg font-bold pb-2">Demo for faster OpenLibrary search</h1>
          <div className="flex flex-row gap-4 pb-2">
            <a className="font-medium text-blue-600 dark:text-blue-500 hover:underline" href="Github">Github</a>
            <a className="font-medium text-blue-600 dark:text-blue-500 hover:underline" href="API">API</a>
          </div>
          <TextInput icon={RiSearch2Line} id="search" type="text" placeholder="Search by book title or isbn" onChange={(e) => (debouncedChangeHandler(e), setSearchTerm(e.target.value))} value={searchTerm} />
          <p className="format pt-2 ml-2 text-xs text-gray-500 font">Search powered by <a href="https://openlibrary.org" target="_blank">OpenLibrary</a></p>
          {searchNotFound &&
            <p className="format pt-2 ml-2 text-md">No results found</p>
          }
          
          <div className={`${showList? "block": "hidden"} relative z-10 bg-white overflow-y-auto max-h-screen max-w-6/12`}>
              {loading ? (
                  loadingPlaceholder.map(function() {
                      return (
                          <div>
                              <div className="grid grid-cols-2 grid-rows-1">
                                  <div className="row-span-2">
                                      <div className="h-24 w-24 bg-gray-300 rounded">
                                          <svg className="h-24 w-24 text-gray-200 dark:text-gray-600" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 20 18">
                                              <path d="M18 0H2a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2Zm-5.5 4a1.5 1.5 0 1 1 0 3 1.5 1.5 0 0 1 0-3Zm4.376 10.481A1 1 0 0 1 16 15H4a1 1 0 0 1-.895-1.447l3.5-7A1 1 0 0 1 7.468 6a.965.965 0 0 1 .9.5l2.775 4.757 1.546-1.887a1 1 0 0 1 1.618.1l2.541 4a1 1 0 0 1 .028 1.011Z"/>
                                          </svg>
                                      </div>
                                  </div>
                                  <div className="col-start-2">
                                      <Skeleton count={2} width={850} />
                                  </div>
                              </div>
                              <hr/>
                          </div>
                      )
                  })
              ): (
                <>
                  {suggestions?.map(function(data) {
                      return (
                          <div key={data.id}>
                          <div className="grid grid-cols-2 grid-rows-1 pt-2">
                              <div className="row-span-2">
                                  <img className="object-contain h-24 w-24" src={"https://covers.openlibrary.org/b/isbn/" + data.isbn +"-M.jpg"} />
                              </div>
                              <div className="col-start-2">
                                  <a href={"https://openlibrary.org/isbn/" + data.isbn} target="_blank">
                                      <p>{data.name}</p>
                                      {data.isbn}
                                  </a>
                              </div>
                          </div>
                          <hr/>
                          </div>
                      )
                  })}
                  
                  </>
              )}
          </div>
      </div>
  )
}

export default App

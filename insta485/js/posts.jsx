import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import PostList from "./postlist";


// The parameter of this function is an object with a string called url inside it.
// url is a prop for the Post component.
export default function Posts({ url }) {
  /* Display image and post owner of a single post */


//   const [imgUrl, setImgUrl] = useState("");
//   const [owner, setOwner] = useState("");
    const [next,setNext] = useState("")
    const [results,setResults] = useState([])



  useEffect(() => {
    // Declare a boolean flag that we can use to cancel the API request.
    let ignoreStaleRequest = false;
    // Call REST API to get the post's information
    fetch(url, { credentials: "same-origin" })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        // If ignoreStaleRequest was set to true, we want to ignore the results of the
        // the request. Otherwise, update the state to trigger a new render.
        console.log(data)
        if (!ignoreStaleRequest) {
        //   setImgUrl(data.imgUrl);
        //   setOwner(data.owner);
            setNext(data.next);
            setResults(data.results);
        }
        console.log("fine")
        console.log(data.results)
        console.log(data.results[0])
        console.log(data.results[0].postid)
        
        
      })
      .catch((error) => console.log(error));


    return () => {
      // This is a cleanup function that runs whenever the Post component
      // unmounts or re-renders. If a Post is about to unmount or re-render, we
      // should avoid updating state.
      ignoreStaleRequest = true;
    };
  }, [url]);

    return (
        <PostList postlist={results}></PostList>
        // <div>
        //     {results}
        // </div>
        // <div>
        //     Hello, I got the message.
        // </div>
    )
   
        
//   );
}

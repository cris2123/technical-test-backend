let readNote = document.querySelector("#read-notes");
let writeNote = document.querySelector("#write-notes");

let URL = "http://localhost:8000/api/v1" 


readNote.addEventListener("click", (event)=> {

  event.preventDefault();
  let token = localStorage.getItem('token')
  
  let bearer = 'Bearer ' + token;

  fetch(URL +'/notes', {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json;charset=utf-8',
      'Authorization': bearer,
    },
    mode: "cors",
  }).then( response => response.json())
  .then( data =>{

    console.log(data);

    let readBlock = document.querySelector("#note-read-content");
    let jsonData = JSON.stringify(data, null, 2);
    readBlock.innerHTML = jsonData;
    

  }).catch(error => {

    console.log(error);
    alert(error);

  });


});


writeNote.addEventListener("click", (event)=>{

  // event.preventDefault();
  // alert("Not implemented");

  let token = localStorage.getItem('token')
  let bearer = 'Bearer ' + token;

  let writeBlock = document.querySelector("#note-write-content");

  
  jsonNote = JSON.parse(writeBlock.innerText);
  jsonNoteObj = JSON.stringify(jsonNote);
  // console.log(jsonNote);

  fetch(URL + '/notes', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json;charset=utf-8',
      'Authorization': bearer,
    },
    body: jsonNoteObj,
    mode: "cors",
  }).then(response => response.json())
    .then(data => {

      console.log(data);
      let writeBlock = document.querySelector("#note-write-content");
      let jsonData = JSON.stringify(data, null, 2);
      writeBlock.innerHTML = `<div> <p>Note created Correctly :</p> ${jsonData} <br/> <p>Clear the window and write a new one</p> </div>`;

    }).catch(error => {

      console.log(error);
      alert(error);

    });



});

let submitButton = document.querySelector("#submit")

const baseURL = "http://localhost:8000/api/v1" 

submitButton.addEventListener("click", (event) => {

  event.preventDefault();

  let loginJson = createLoginJson(document.querySelector(".login-form"))

  fetch(baseURL+"/login",{
    method: 'POST',
    headers: {
      'Content-Type': 'application/json;charset=utf-8'
    },
    body: loginJson,
    mode: "cors",
  }).then( response => response.json())
  .then(data => {

    if(data.token){

      localStorage.setItem('token', data.token);
      console.log(localStorage.getItem('token'));
      window.location = "http://localhost:5000/main";
    }   
  }).catch(error => {

    console.log(error);
    alert("Error when authenticating user");

  });

  
  
  // Here fetch api to get data from response store token on local storage

  
  
})

function createLoginJson(elementData){

  arrayFormFields = Array.from(elementData);

  loginObj = {}
  for (let elem of arrayFormFields) {

    if(elem.type != "submit") {
      loginObj[elem.name] = elem.value;
    }
  }

  return JSON.stringify(loginObj);


}
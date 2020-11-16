// Handles submission of input data without refreshing the page, listens for onclick or enter event
// then calls handleSubmission() and fires this data to the "/" route where it is then dealt w/ and adedd
// to database

function handleSubmission() {
    user_input = home_input.value;
    home_input.value = "";
    $.ajax({
        data : { user_input : user_input},
        type : "POST",
        url : '/'
    })
}

var element = document.getElementById("home_button_submit");
if (element.addEventListener)
    element.addEventListener("click", handleSubmission, false);

const home_input = document.getElementById("user_entry");
home_input.addEventListener("keyup", function(event) {
    if (event.key === "Enter") {
        handleSubmission();
    }
});
const hour = new Date().getHours();
let message = "";
			
if (hour >= 6 && hour < 12) {
    message = "Good Morning, Cyber Explorer!";
} else if (hour >= 12 && hour < 18) {
    message = "Good Afternoon, Cyber Defender!";
} else if (hour >= 18) {
    message = "Good Evening, Cyber Dweller!";
} else {
    message = "The Night is Long.. And Full of Terrors!";
}

console.log(message);
document.querySelector("h1").textContent = message;

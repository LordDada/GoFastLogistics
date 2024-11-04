const rateChart = {
    "Bangalore": [100, 150, 200, 250, 300, 350, 400, 450, 500, 550],
    "Delhi": [100, 150, 200, 250, 300, 350, 400, 450, 500, 550],
    "Mumbai": [100, 150, 200, 250, 300, 350, 400, 450, 500, 550],
    "Ghy": [140, 190, 240, 290, 340, 390, 440, 490, 540, 590]
};

function calculateRate() {
    const weight = parseInt(document.getElementById("weight").value);
    const destination = document.getElementById("destination").value;

    const rate = rateChart[destination][weight - 1];
    document.getElementById("result").textContent = `The rate for ${weight} Kg to ${destination} is ₹${rate}`;
}

window.onload = () => {
    console.log("🚀 Book Finder Loaded");

    const cards = document.querySelectorAll(".book-card");
    cards.forEach((card, index) => {
        card.style.opacity = "0";
        setTimeout(() => {
            card.style.opacity = "1";
        }, index * 200);
    });
};


function showMessage(msg) {
    alert(msg);
}

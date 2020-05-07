document.addEventListener('DOMContentLoaded', (event) => {
    const { GoogleSpreadsheet } = require('google-spreadsheet');
    const doc = new GoogleSpreadsheet('1bVeOB_WMFPJSfqreMl7-jkSe5Su0NlS3s4L7fUUMbiY/');
    const creds = require('./client_secret.json');
    const charactersList = document.getElementById('charactersList');
    const searchBar = document.getElementById('searchBar');
    const searchWrapper = document.getElementById('searchWrapper');
    const pageTitle = document.getElementById('pageTitle');
    const citation = document.getElementById('citation');
    const webChart = document.getElementById('myChart');
    const imageHTML = document.getElementById('imageHTML');
    const descriptionHTML = document.getElementById('description');
    const timestampHTML = document.getElementById('timestamp');
    const fetchedHTML = document.getElementById('fetched');
    const backButton = document.getElementById('backButton');
    webChart.style.display = 'none';
    imageHTML.style.display = 'none';
    descriptionHTML.style.display = 'none';
    timestampHTML.style.display = 'none';
    fetchedHTML.style.display = 'none';
    backButton.style.display = 'none';
    let data = [];

    function preloadImage (img) {
        const src = img.getAttribute('data-lazy');
        if(!src) {
            return;
        }
        img.src = src;
    }
    function lazyLoading(){
        const images = document.querySelectorAll("[data-lazy]");
            const imgOptions = {
                threshold: 0,
                rootMargin: "0px 0px 5000px 0px"
            };
            const imgObserver = new IntersectionObserver((entries, imgObserver) => {
                entries.forEach(entry => {
                    if(!entry.isIntersecting){
                        return;
                    } else {
                        preloadImage(entry.target);
                        imgObserver.unobserve(entry.target)
                    }
                })
            }, imgOptions);
            images.forEach(image => {
                imgObserver.observe(image);
            })
    }

    searchBar.addEventListener('keyup', (e) => {
        const searchString = e.target.value.toLowerCase();
        if(searchString){
            let filteredCharacters = [];
            for (i = 0; i < data.length; i++) {
                let addFlag = true;
                let character = data[i];
                let search_str = character.name.toLowerCase();
                for(j = 0; j < searchString.length; j++){
                    if(search_str[j] != searchString[j]){
                        addFlag = false;
                        break;
                    }
                }
                if(addFlag){
                    filteredCharacters.push(character);
                }
            }    
            displayCharacters(filteredCharacters);
            lazyLoading();
        }
        else{
            displayCharacters(data);
            lazyLoading();
        }
    });

    const loadCharacters = async () => {
        try {
            data = await accessSpreadsheet();
            displayCharacters(data);
            lazyLoading();
        } catch (err) {
            console.error(err);
        }
    };

    const displayCharacters = (characters) => {
        var cnt = 0;
        const htmlString = characters
            .map((character) => {
                return `
                    <li class="character"">
                        <h2>${character.name}</h2>
                        <p>Status: ${character.status}</p>
                        <img data-lazy="${character.image}" id="${character.name}" height="100px" width="100px" onerror="this.onerror=null;this.src='//logo.clearbit.com/clearbit.com?size=100&greyscale=true';" style="cursor: pointer;"></img>
                    </li>
            `;
            })
            .join('');
        charactersList.innerHTML = htmlString;
    };
    async function accessSpreadsheet() {
        await doc.useServiceAccountAuth({
            client_email: creds.client_email,
            private_key: creds.private_key,
            });
            await doc.loadInfo(); // loads document properties and worksheets
            const sheet = doc.sheetsByIndex[0]; // or use doc.sheetsById[id]
            const rows = await sheet.getRows({
                offset: 2
            });
            let customRowOBJ = []
            rows.forEach(row =>{
                image_link = '//logo.clearbit.com/' + row.name +'.com?size=100'
                let custom = {name: row.name, status: row.status, description:row.description, date: row.date, time: row.time, image: image_link, from: sheet.title};
                customRowOBJ.push(custom);
            });
            return customRowOBJ;
    }
    function getDataByName(selected_name){
        for (var i=0; i < data.length; i++) {
            if (data[i].name === selected_name) {
                return data[i];
            }
        }
    }
    function showChart(data, xlabels){
        var ctx = document.getElementById('myChart').getContext('2d');
        var chart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: xlabels,
                datasets: data
            },
            options: {
                scales: {
                    xAxes: [{ stacked: true }],
                    yAxes: [{ stacked: true }]
                  }
            }
        });
    }

    loadCharacters();

    document.getElementById("charactersList").addEventListener("click",function(e) {
        if(e.target && e.target.nodeName == "IMG") {
            searchWrapper.style.display = 'none';
            searchBar.style.display = 'none';
            charactersList.style.display = 'none';
            //pageTitle.style.display = 'block';
            citation.style.display = 'none';
            backButton.style.display = 'block';
            webChart.style.display = 'block';
            descriptionHTML.style.display = 'block';
            timestampHTML.style.display = 'block';
            fetchedHTML.style.display = 'block';
            imageHTML.style.display = 'block';
            imageHTML.src = '';
            imageHTML.alt = '';
            descriptionHTML.innerHTML = '';
            timestampHTML.innerHTML = '';
            fetchedHTML.innerHTML = '';

            let selectedInfo = getDataByName(String(e.target.id));
            pageTitle.innerHTML = selectedInfo.name;
            if(selectedInfo.description){
                descriptionHTML.innerHTML = 'Description: ' + selectedInfo.description; 
            }
            else{
                descriptionHTML.innerHTML = 'Description: N/A';
            }
            timestampHTML.innerHTML = 'Last Updated: ' + selectedInfo.time + ', ' + selectedInfo.date;
            fetchedHTML.innerHTML = 'Fetched: ' + selectedInfo.from;
            imageHTML.src = selectedInfo.image;
            imageHTML.alt = 'Hi';
            imageHTML.style.display = 'block';
            x_axis_labels = [selectedInfo.from];
            console.log(x_axis_labels);
            pre_data = selectedInfo.status.split(',');
            post_data = [];
            for (i = 0; i < pre_data.length; i++) {
                let val = pre_data[i];
                if(val.toLowerCase() == "layoffs"){
                    post_data.push({
                        label: 'Layoffs',
                        data: [1],
                        backgroundColor: '#FF0000' // red
                      });
                }
                else if(val.toLowerCase() == "offers rescinded"){
                    post_data.push({
                        label: 'Offers Rescinded',
                        data: [1],
                        backgroundColor: '#FFFF00' // yellow
                      });
                }
                else if(val.toLowerCase() == "hiring freeze"){
                    post_data.push({
                        label: 'Hiring Freeze',
                        data: [1],
                        backgroundColor: '#D6E9C6' // green
                      });
                }  
                else if(val.toLowerCase() == "hiring"){
                    post_data.push({
                        label: 'Hiring',
                        data: [1],
                        backgroundColor: '#228B22' // green
                      });
                }
            }
            console.log('post_data: ' + post_data);
            showChart(post_data, x_axis_labels);
        }
    });

    document.getElementById("backButton").addEventListener("click",function(e) {
            searchWrapper.style.display = 'block';
            searchBar.style.display = 'block';
            charactersList.style.display = 'grid';
            pageTitle.style.display = 'block';
            citation.style.display = 'none';
            webChart.style.display = 'none';
            descriptionHTML.style.display = 'none';
            timestampHTML.style.display = 'none';
            fetchedHTML.style.display = 'none';
            imageHTML.style.display = 'none';
            backButton.style.display = 'none';
    });

    imageHTML.onerror = function() {
        this.src = '//logo.clearbit.com/clearbit.com?size=100&greyscale=true'
    }
});
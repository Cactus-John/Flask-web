fetch('/artists')
    .then(response => response.json())
    .then(songs => {
        const songList = document.getElementById('song-list');

        songs.forEach(song => {
            const listItem = document.createElement('li');
            listItem.textContent = song.title;
            songList.appendChild(listItem);
        });
    });

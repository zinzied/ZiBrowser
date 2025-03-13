class VideoHandler {
    constructor() {
        this.store = new ChromeStore();
        // Request 1GB of storage
        this.store.init(1024 * 1024 * 1024, (store) => {
            console.log('Video storage initialized');
        });
    }

    saveVideo(videoUrl, filename) {
        return new Promise((resolve, reject) => {
            this.store.getAndWrite(
                videoUrl,
                `videos/${filename}`,
                'video/mp4',
                { create: true },
                (fileEntry) => {
                    resolve(fileEntry);
                }
            );
        });
    }

    getVideoUrl(filename) {
        return new Promise((resolve, reject) => {
            this.store.getFile(`videos/${filename}`, {}, (fileEntry) => {
                resolve(fileEntry.toURL());
            });
        });
    }
}
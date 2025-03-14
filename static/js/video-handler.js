class VideoStore {
    constructor() {
        this.fs = null;
        this.QUOTA = 1024 * 1024 * 1024; // 1GB storage
    }

    init() {
        return new Promise((resolve, reject) => {
            window.webkitRequestFileSystem(
                window.PERSISTENT,
                this.QUOTA,
                (fs) => {
                    this.fs = fs;
                    resolve(this);
                },
                (error) => {
                    console.error('Error initializing filesystem:', error);
                    reject(error);
                }
            );
        });
    }

    saveVideo(videoUrl, filename) {
        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();
            xhr.open('GET', videoUrl, true);
            xhr.responseType = 'blob';

            xhr.onload = () => {
                if (xhr.status === 200) {
                    const blob = xhr.response;
                    this.fs.root.getFile(filename, { create: true }, (fileEntry) => {
                        fileEntry.createWriter((writer) => {
                            writer.onwriteend = () => resolve(fileEntry);
                            writer.onerror = (error) => reject(error);
                            writer.write(blob);
                        });
                    });
                } else {
                    reject(new Error(`Failed to download video: ${xhr.status}`));
                }
            };
            xhr.send();
        });
    }

    getVideoUrl(filename) {
        return new Promise((resolve, reject) => {
            this.fs.root.getFile(filename, {}, (fileEntry) => {
                resolve(fileEntry.toURL());
            }, reject);
        });
    }
}
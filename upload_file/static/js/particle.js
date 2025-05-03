function initFileUpload() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    const selectBtn = document.getElementById('selectBtn');
    const uploadBtn = document.getElementById('uploadBtn');

    if (!uploadArea || !fileInput || !selectBtn || !uploadBtn) return;

    uploadArea.addEventListener('click', () => fileInput.click());
    selectBtn.addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', function() {
        if (this.files.length) {
            selectBtn.style.display = 'none';
            uploadBtn.style.display = 'inline-block';

            const fileName = this.files[0].name;
            const fileInfo = document.createElement('p');
            fileInfo.textContent = `Selected: ${fileName}`;
            fileInfo.style.marginTop = '10px';
            fileInfo.style.color = '#4361ee';
            uploadArea.appendChild(fileInfo);
        }
    });

    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = '#4361ee';
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.style.borderColor = '#ddd';
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = '#ddd';

        if (e.dataTransfer.files.length) {
            fileInput.files = e.dataTransfer.files;
            const event = new Event('change');
            fileInput.dispatchEvent(event);
        }
    });
}

function initParticles() {
    if (!document.getElementById('particles-js')) return;

    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/particles.js/2.0.0/particles.min.js';
    
    script.onload = function() {
        particlesJS('particles-js', {
            particles: {
                number: { value: 60, density: { enable: true, value_area: 800 } },
                color: { value: "#4361ee" },
                opacity: { 
                    value: 0.5, 
                    random: true, 
                    anim: { enable: true, speed: 1, opacity_min: 0.1 } 
                },
                size: { 
                    value: 3, 
                    random: true, 
                    anim: { enable: true, speed: 2, size_min: 0.1 } 
                },
                line_linked: { 
                    enable: true, 
                    distance: 150, 
                    color: "#4361ee", 
                    opacity: 0.3, 
                    width: 1 
                },
                move: { 
                    enable: true, 
                    speed: 2, 
                    direction: "none", 
                    random: true, 
                    out_mode: "out" 
                }
            },
            interactivity: {
                detect_on: "window",
                events: {
                    onhover: { enable: true, mode: "repulse" },
                    onclick: { enable: true, mode: "push" },
                    resize: true
                },
                modes: {
                    repulse: { distance: 80, duration: 0.4 },
                    push: { particles_nb: 4 }
                }
            },
            retina_detect: true
        });
    }; 
    document.body.appendChild(script);
}

document.addEventListener('DOMContentLoaded', function() {
    initFileUpload();
    initParticles();
});
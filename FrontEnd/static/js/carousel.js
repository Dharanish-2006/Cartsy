/**
 * Product Image Carousel with Lightbox
 * Features: Bootstrap carousel, lightbox modal, zoom on desktop/mobile
 */

class ProductCarousel {
    constructor(productData, containerId = "carousel-container") {
        this.product = productData;
        this.containerId = containerId;
        this.currentImageIndex = 0;
        this.zoomLevel = 1;
        this.init();
    }

    init() {
        if (!this.product || !this.product.images || this.product.images.length === 0) {
            console.warn("No images found for carousel");
            return;
        }
        this.render();
        this.attachEventListeners();
    }

    render() {
        const container = document.getElementById(this.containerId);
        if (!container) {
            console.error(`Container with id "${this.containerId}" not found`);
            return;
        }

        // Build carousel HTML
        const carouselHTML = this.buildCarouselHTML();
        container.innerHTML = carouselHTML;
    }

    buildCarouselHTML() {
        const images = this.product.images;
        const primaryImage = images[0];

        // Carousel indicators
        const indicators = images
            .map(
                (img, idx) =>
                    `<button type="button" data-bs-target="#productCarousel" data-bs-slide-to="${idx}" 
                     class="carousel-indicator" ${idx === 0 ? 'aria-current="true"' : ""} 
                     aria-label="Slide ${idx + 1}" style="cursor: pointer; height: 8px; width: 8px; margin: 0 4px;"></button>`
            )
            .join("");

        // Carousel items
        const items = images
            .map(
                (img, idx) =>
                    `<div class="carousel-item ${idx === 0 ? "active" : ""}">
                     <img src="${img.image}" class="d-block w-100 carousel-image" 
                          alt="Product image ${idx + 1}" style="cursor: pointer; max-height: 500px; object-fit: cover;">
                     </div>`
            )
            .join("");

        const html = `
            <div id="productCarousel" class="carousel slide" data-bs-ride="carousel">
                <!-- Indicators -->
                <div class="carousel-indicators" style="background: rgba(0,0,0,0.5); border-radius: 10px; padding: 10px; justify-content: center;">
                    ${indicators}
                </div>

                <!-- Carousel items -->
                <div class="carousel-inner">
                    ${items}
                </div>

                <!-- Controls -->
                <button class="carousel-control-prev" type="button" data-bs-target="#productCarousel" data-bs-slide="prev"
                    style="background: linear-gradient(to right, rgba(0,0,0,0.5), transparent); border-radius: 5px;">
                    <span class="carousel-control-prev-icon" aria-hidden="true"></span>
                    <span class="visually-hidden">Previous</span>
                </button>
                <button class="carousel-control-next" type="button" data-bs-target="#productCarousel" data-bs-slide="next"
                    style="background: linear-gradient(to left, rgba(0,0,0,0.5), transparent); border-radius: 5px;">
                    <span class="carousel-control-next-icon" aria-hidden="true"></span>
                    <span class="visually-hidden">Next</span>
                </button>

                <!-- Click for lightbox hint -->
                <div style="text-align: center; margin-top: 10px; font-size: 12px; color: #666;">
                    Click image to zoom
                </div>
            </div>

            <!-- Lightbox Modal -->
            <div class="modal fade" id="imageLightbox" tabindex="-1" aria-labelledby="imageLightboxLabel" aria-hidden="true">
                <div class="modal-dialog modal-xl modal-dialog-centered">
                    <div class="modal-content" style="background: #000; border: none;">
                        <!-- Close button -->
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"
                            style="position: absolute; top: 10px; right: 10px; z-index: 1050;"></button>

                        <div class="modal-body p-0" style="position: relative;">
                            <!-- Lightbox image container with zoom -->
                            <div class="lightbox-image-container" style="
                                overflow: auto;
                                background: #000;
                                display: flex;
                                align-items: center;
                                justify-content: center;
                                min-height: 500px;
                                position: relative;
                            ">
                                <img id="lightboxImage" src="" alt="Zoomed product image" 
                                    style="max-width: 100%; max-height: 600px; cursor: zoom-in; touch-action: pinch-zoom;"
                                    class="lightbox-img">
                            </div>

                            <!-- Lightbox controls -->
                            <div style="
                                display: flex;
                                justify-content: space-between;
                                align-items: center;
                                background: rgba(0,0,0,0.8);
                                padding: 15px;
                                gap: 10px;
                            ">
                                <!-- Previous button -->
                                <button class="btn btn-sm btn-light lightbox-prev" style="min-width: 100px;">
                                    <i class="bi bi-chevron-left"></i> Previous
                                </button>

                                <!-- Zoom controls -->
                                <div class="d-flex align-items-center gap-2">
                                    <button class="btn btn-sm btn-light" id="zoomOut" style="min-width: 40px;">−</button>
                                    <span id="zoomLevel" style="color: white; min-width: 50px; text-align: center;">100%</span>
                                    <button class="btn btn-sm btn-light" id="zoomIn" style="min-width: 40px;">+</button>
                                    <button class="btn btn-sm btn-light" id="resetZoom" style="min-width: 60px;">Reset</button>
                                </div>

                                <!-- Next button -->
                                <button class="btn btn-sm btn-light lightbox-next" style="min-width: 100px;">
                                    Next <i class="bi bi-chevron-right"></i>
                                </button>
                            </div>

                            <!-- Image counter -->
                            <div style="
                                text-align: center;
                                background: rgba(0,0,0,0.8);
                                color: white;
                                padding: 8px;
                                font-size: 12px;
                            ">
                                <span id="imageCounter">1 / ${images.length}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        return html;
    }

    attachEventListeners() {
        // Click image to open lightbox
        document.querySelectorAll(".carousel-image").forEach((img) => {
            img.addEventListener("click", () => {
                this.openLightbox(img.src);
            });
        });

        // Lightbox zoom controls
        document.getElementById("zoomIn")?.addEventListener("click", () => this.zoomImage(0.1));
        document.getElementById("zoomOut")?.addEventListener("click", () => this.zoomImage(-0.1));
        document.getElementById("resetZoom")?.addEventListener("click", () => this.resetZoom());

        // Lightbox navigation
        document.querySelector(".lightbox-prev")?.addEventListener("click", () => this.prevImage());
        document.querySelector(".lightbox-next")?.addEventListener("click", () => this.nextImage());

        // Update lightbox image when carousel changes
        const carousel = document.getElementById("productCarousel");
        if (carousel) {
            carousel.addEventListener("slide.bs.carousel", (e) => {
                this.currentImageIndex = e.to;
                const lightboxModal = document.getElementById("imageLightbox");
                if (lightboxModal.classList.contains("show")) {
                    this.updateLightboxImage();
                }
            });
        }

        // Mobile pinch-to-zoom support
        this.setupPinchZoom();
    }

    openLightbox(imageSrc) {
        const lightboxImage = document.getElementById("lightboxImage");
        if (lightboxImage) {
            lightboxImage.src = imageSrc;
            this.zoomLevel = 1;
            this.updateZoomUI();
        }

        // Get active carousel item index
        const carousel = document.getElementById("productCarousel");
        const activeItem = carousel?.querySelector(".carousel-item.active");
        if (activeItem) {
            this.currentImageIndex = Array.from(carousel.querySelectorAll(".carousel-item")).indexOf(activeItem);
        }

        const lightboxModal = new bootstrap.Modal(document.getElementById("imageLightbox"));
        lightboxModal.show();
    }

    updateLightboxImage() {
        const images = this.product.images;
        const image = images[this.currentImageIndex];
        const lightboxImage = document.getElementById("lightboxImage");
        if (lightboxImage && image) {
            lightboxImage.src = image.image;
            document.getElementById("imageCounter").textContent = 
                `${this.currentImageIndex + 1} / ${images.length}`;
        }
    }

    zoomImage(step) {
        this.zoomLevel = Math.max(1, Math.min(3, this.zoomLevel + step));
        this.updateZoomUI();
    }

    resetZoom() {
        this.zoomLevel = 1;
        this.updateZoomUI();
    }

    updateZoomUI() {
        const lightboxImage = document.getElementById("lightboxImage");
        const zoomLevelDisplay = document.getElementById("zoomLevel");
        if (lightboxImage) {
            lightboxImage.style.transform = `scale(${this.zoomLevel})`;
            lightboxImage.style.cursor = this.zoomLevel > 1 ? "grab" : "zoom-in";
        }
        if (zoomLevelDisplay) {
            zoomLevelDisplay.textContent = Math.round(this.zoomLevel * 100) + "%";
        }
    }

    prevImage() {
        this.currentImageIndex = (this.currentImageIndex - 1 + this.product.images.length) % this.product.images.length;
        this.updateLightboxImage();
    }

    nextImage() {
        this.currentImageIndex = (this.currentImageIndex + 1) % this.product.images.length;
        this.updateLightboxImage();
    }

    setupPinchZoom() {
        const container = document.querySelector(".lightbox-image-container");
        const img = document.getElementById("lightboxImage");

        if (!container || !img) return;

        let lastDistance = 0;

        container.addEventListener(
            "touchmove",
            (e) => {
                if (e.touches.length === 2) {
                    e.preventDefault();

                    const dx = e.touches[0].clientX - e.touches[1].clientX;
                    const dy = e.touches[0].clientY - e.touches[1].clientY;
                    const distance = Math.sqrt(dx * dx + dy * dy);

                    if (lastDistance > 0) {
                        const scale = distance / lastDistance;
                        this.zoomLevel = Math.max(1, Math.min(3, this.zoomLevel * scale));
                        this.updateZoomUI();
                    }
                    lastDistance = distance;
                }
            },
            false
        );

        container.addEventListener("touchend", () => {
            lastDistance = 0;
        });

        // Hover zoom on desktop (optional enhancement)
        img.addEventListener("wheel", (e) => {
            if (e.ctrlKey || e.metaKey) {
                e.preventDefault();
                const step = e.deltaY > 0 ? -0.1 : 0.1;
                this.zoomImage(step);
            }
        });
    }
}

// Auto-initialize if product data is available in window
if (typeof window.productData !== "undefined") {
    document.addEventListener("DOMContentLoaded", () => {
        new ProductCarousel(window.productData);
    });
}

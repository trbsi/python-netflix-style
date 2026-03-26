function loadVideos(){

    if(loading) return;

    loading = true;

    $(".load-more-btn .button-text").text("Loading...");

    if (lastId) {
        api_url += `&last_id=${lastId}`;
    }

    $.get(api_url, function(data) {

        data.videos.forEach(function(video){
            lastId = video.id;
            let categories = "";

            video.categories.forEach(function(cat){
                categories += `<a href="/media/categories/${cat.slug}" class="font-size-14">${cat.title}</a> | `;
            });

            let html = `
            <div class="col">
                <div class="iq-card card-hover">
                    <div class="block-images position-relative w-100">

                        <div class="img-box w-100">
                            <a href="${video.url}">
                                <img src="${video.thumbnail}" class="img-fluid object-cover w-100 d-block border-0 rounded-3">
                            </a>
                        </div>

                        <div class="card-description with-transition">

                            <ul class="genres-list p-0 mb-2 d-flex align-items-center flex-wrap list-inline">
                                <li class="fw-semi-bold">${categories}</li>
                            </ul>

                            <div class="cart-content">
                                <div class="content-left">

                                    <h5 class="iq-title text-capitalize">
                                        <a href="${video.url}">${video.title}</a>
                                    </h5>

                                    <div class="d-flex align-items-center gap-3">
                                        <small class="font-size-12">${video.duration}</small>
                                    </div>

                                </div>
                            </div>

                            <div class="d-flex align-items-center justify-content-center gap-2 mt-3">
                                <div class="iq-play-button iq-button">
                                    <a href="${video.url}" class="btn btn-primary w-100">Play Now</a>
                                </div>
                            </div>

                        </div>
                    </div>
                </div>
            </div>
            `;

            $("#videos-container").append(html);

        });

        if(data.has_next === false){
            $(".load-more-btn").hide();
        }

        loading = false;
        $(".load-more-btn .button-text").text("Load More");
    });
}

$(document).ready(function(){

    // load first page
    loadVideos();

    // load next page on click
    $(".load-more-btn").click(function(){
        loadVideos();
    });

});

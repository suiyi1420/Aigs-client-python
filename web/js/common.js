function openModal(url){
    $("#Modal").find(".modal-content").empty();
    $("#Modal").modal({
        show:true,
        remote:url
    });
   // $("#myModalLabel").text(title);
}
$("#Modal").on("hidden.bs.modal", function() {
    $(this).removeData("bs.modal");
});
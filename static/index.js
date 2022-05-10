$(document).ready(function() { // opens reviews
    $(document).on('click',".product_display", function(){
        if ($("div").hasClass("expanded") === true){
            console.log("You can only expand one")
        }
        else{
            if ($(this).hasClass("expanded")){
                return;
            }
            else {
                $(this).addClass("expanded");
                $(".reviews").addClass("expanded");
                $(this).parent().addClass("expandedParent");
            }
        }
    })
})


function closeEdit(){   // closes the reviews
    $(document).remove("modifyButtons");
    $(".modifyButtons").remove();
    $("div").removeClass("expanded");
    $("article").removeClass("expandedParent");
};
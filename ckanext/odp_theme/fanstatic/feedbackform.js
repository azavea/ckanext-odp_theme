
function registerCheckbox(checkboxSelector, textfieldSelector) {
    var checkbox = $(checkboxSelector);
    checkbox.change(function() {
        if (checkbox[0].checked) {
            $(textfieldSelector).show();
        } else {
            $(textfieldSelector).hide();
        }
    });
    checkbox.trigger('change');
}

registerCheckbox('#checkbox-economic', '#text-economic');
registerCheckbox('#checkbox-social', '#text-social');
registerCheckbox('#checkbox-public-service', '#text-public-service');
registerCheckbox('#checkbox-other', '#text-other');

// i18n for labels?
// maybe move labels to templates after all?

(function($){$(function(){

    class PBoxItem {
        update(pbox) {
            if (this.isAvailable(pbox)) {
                pbox.showButton(this, this.label, this.pboxClass);
            }
        }
    }


    class LoginPBI extends PBoxItem {
        label = 'ZALOGUJ';
        pboxClass = 'zakladka-tool_login';

        isAvailable(pbox) {
            return true;
        }
        
        action() {
            alert('akcja');
        }
    }


    class BookmarkPBI extends PBoxItem {
        label = 'DODAJ ZAKŁADKĘ'
        
    }
    

    $.pbox.addItem(new LoginPBI());


})})(jQuery);

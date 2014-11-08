<%namespace file="../notes/common.mak" import="notes_selector"/>
<%namespace file="../tasks/common.mak" import="tasks_selector"/>
<%
    _id = h.common.gen_id()
    _combobox_container = "combobox-%s" % _id
%>
<div class="dl60 easyui-dialog"
    title="${title}"
    data-options="
        modal:true,
        draggable:false,
        resizable:false,
        iconCls:'fa fa-pencil-square-o'
    ">
    ${h.tags.form(request.url, class_="_ajax %s" % ('readonly' if readonly else ''), autocomplete="off")}
        <div class="easyui-tabs" data-options="border:false,height:400">
            <div title="${_(u'Main')}">
                <div class="form-field">
                    <div class="dl15">
                        ${h.tags.title(_(u"name"), True, "name")}
                    </div>
                    <div class="ml15">
                        ${h.tags.text("name", item.name if item else None, class_="easyui-textbox w20")}
                        ${h.common.error_container(name='name')}
                    </div>
                </div>
                <div class="form-field">
                    <div class="dl15">
                        ${h.tags.title(_(u"account"), True, "account_id")}
                    </div>
                    <div class="ml15">
                        ${h.fields.accounts_combobox_field(
                        	request, item.account_id if item else None,
                        	show_toolbar=(not readonly if readonly else True)
                        )}
                        ${h.common.error_container(name='account_id')}
                    </div>
                </div>
                <div class="form-field">
                    <div class="dl15">
                        ${h.tags.title(_(u"subaccount type"), True, "subaccount_type")}
                    </div>
                    <div class="ml15">
                        ${h.fields.subaccounts_types_combobox_field(
                            resource.resource_type.name if resource else None, 
                            options="""
                                width:271,
                                onSelect: function(record){
                                    $.post("/" + record.value + "/combobox",
                                    	{'name': 'source_id'},
                                        function(data){
                                            $("#%s").html(data);
                                            $.parser.parse("#%s");
                                        }
                                    );
                                },
                                onLoadSuccess: function(){
                                	var subaccount_type = $(this).combobox('getValue');
                                    $.post("/" + subaccount_type + "/combobox",
                                    	{'name': 'source_id', 'resource_id': %s},
                                        function(data){
			                    data = $('<div />').html(data);
			                    if(%s){
                                                data.find('.combogrid-toolbar').remove();
                                                data = disable_obj_inputs(data);
			                    }
                                            data = data.html();
                                            $("#%s").html(data);
                                            $.parser.parse("#%s");
                                        }
                                    );
                                }                          
                            """ % (
                           	_combobox_container, _combobox_container,
                            	resource.id if resource else 0,
			        h.common.jsonify(readonly if readonly else False),
                            	_combobox_container, _combobox_container,
                            )
                        )}
                        ${h.common.error_container(name='subaccount_type')}
                    </div>
                </div>
                <div class="form-field">
                    <div class="dl15">
                        ${h.tags.title(_(u"subaccount object"), True, "source_id")}
                    </div>
                    <div class="ml15">
                        <span id="${_combobox_container}"></span>
                        ${h.common.error_container(name='source_id')}
                    </div>
                </div>
                <div class="form-field mb05">
                    <div class="dl15">
                         ${h.tags.title(_(u"description"), False, "descr")}
                    </div>
                    <div class="ml15">
                        ${h.tags.text("descr", item.descr if item else None, class_="easyui-textbox w20", data_options="multiline:true,height:80")}
                        ${h.common.error_container(name='descr')}
                    </div>
                </div>
            </div>
            <div title="${_(u'Notes')}">
                <div class="easyui-panel" data-options="fit:true,border:false">
                    ${notes_selector(
                        values=([note.id for note in item.resource.notes] if item else []),
                        can_edit=(
                            not (readonly if readonly else False) and 
                            (_context.has_permision('add') if item else _context.has_permision('edit'))
                        ) 
                    )}
                </div>
            </div>
            <div title="${_(u'Tasks')}">
                <div class="easyui-panel" data-options="fit:true,border:false">
                    ${tasks_selector(
                        values=([task.id for task in item.resource.tasks] if item else []),
                        can_edit=(
                            not (readonly if readonly else False) and 
                            (_context.has_permision('add') if item else _context.has_permision('edit'))
                        ) 
                    )}
                </div>
            </div>
        </div>
        <div class="form-buttons">
            <div class="dl20 status-bar"></div>
            <div class="ml20 tr button-group">
                ${h.tags.submit('save', _(u"Save"), class_="button")}
                ${h.common.reset('cancel', _(u"Cancel"), class_="button danger")}
            </div>
        </div>
    ${h.tags.end_form()}
</div>

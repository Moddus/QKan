<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis hasScaleBasedVisibilityFlag="0" version="3.22.4-Białowieża" maxScale="0" readOnly="0" styleCategories="LayerConfiguration|Symbology|Labeling|Fields|Forms|Actions|MapTips|AttributeTable|Rendering|CustomProperties|Temporal|Legend|Notes" minScale="1e+08">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
    <Private>0</Private>
  </flags>
  <temporal limitMode="0" startField="" endField="" enabled="0" accumulate="0" durationField="" startExpression="" durationUnit="min" endExpression="" mode="0" fixedDuration="0">
    <fixedRange>
      <start></start>
      <end></end>
    </fixedRange>
  </temporal>
  <customproperties>
    <Option type="Map">
      <Option type="List" name="dualview/previewExpressions">
        <Option type="QString" value="&quot;name&quot;"/>
      </Option>
      <Option type="int" name="embeddedWidgets/count" value="0"/>
      <Option name="variableNames"/>
      <Option name="variableValues"/>
    </Option>
  </customproperties>
  <legend type="default-vector" showLabelLegend="0"/>
  <fieldConfiguration>
    <field name="pk" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="warntext" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="warntyp" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="warnlevel" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="layername" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="attrname" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="objname" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="createdat" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <aliases>
    <alias index="0" field="pk" name=""/>
    <alias index="1" field="warntext" name="Warntext"/>
    <alias index="2" field="warntyp" name="Warntyp"/>
    <alias index="3" field="warnlevel" name="Warnlevel"/>
    <alias index="4" field="layername" name="Layername"/>
    <alias index="5" field="attrname" name="Attributname"/>
    <alias index="6" field="objname" name="Objektname"/>
    <alias index="7" field="createdat" name="bearbeitet"/>
  </aliases>
  <defaults>
    <default expression="" field="pk" applyOnUpdate="0"/>
    <default expression="" field="warntext" applyOnUpdate="0"/>
    <default expression="" field="warntyp" applyOnUpdate="0"/>
    <default expression="" field="warnlevel" applyOnUpdate="0"/>
    <default expression="" field="layername" applyOnUpdate="0"/>
    <default expression="" field="attrname" applyOnUpdate="0"/>
    <default expression="" field="objname" applyOnUpdate="0"/>
    <default expression=" format_date( now(), 'yyyy-MM-dd HH:mm:ss')" field="createdat" applyOnUpdate="0"/>
  </defaults>
  <constraints>
    <constraint constraints="3" field="pk" unique_strength="2" notnull_strength="2" exp_strength="0"/>
    <constraint constraints="0" field="warntext" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="warntyp" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="warnlevel" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="layername" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="attrname" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="objname" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="createdat" unique_strength="0" notnull_strength="0" exp_strength="0"/>
  </constraints>
  <constraintExpressions>
    <constraint desc="" exp="" field="pk"/>
    <constraint desc="" exp="" field="warntext"/>
    <constraint desc="" exp="" field="warntyp"/>
    <constraint desc="" exp="" field="warnlevel"/>
    <constraint desc="" exp="" field="layername"/>
    <constraint desc="" exp="" field="attrname"/>
    <constraint desc="" exp="" field="objname"/>
    <constraint desc="" exp="" field="createdat"/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction key="Canvas" value="{00000000-0000-0000-0000-000000000000}"/>
    <actionsetting isEnabledOnlyWhenEditable="0" type="1" id="{ce7efdcf-811f-4b6b-859e-b64a436a7a74}" notificationMessage="" name="Zoom/Pan zum Objekt" icon="C:/FHAC/hoettges/Kanalprogramme/QKan/qkan/datacheck/jump.png" capture="1" shortTitle="Zoom/Pan zum Objekt" action="from qgis.PyQt import QtWidgets&#xa;from qgis.core import Qgis&#xa;&#xa;obj = '[%objname%]'&#xa;attr = '[%attrname%]'&#xa;&#xa;activeproject = QgsProject().instance()&#xa;layername = '[%layername%]'&#xa;clayers = activeproject.mapLayersByName(layername)&#xa;if not clayers:&#xa;    QtWidgets.QMessageBox.information(None, &quot;Fehler im Programmcode der Aktion&quot;, f'Layer &quot;{layername}&quot;nicht definiert')&#xa;else:&#xa;    clayer = clayers[0]&#xa;    clayer.selectByExpression(f&quot;{attr} = '{obj}'&quot;)&#xa;    qgis.utils.iface.setActiveLayer(clayer)&#xa;    qgis.utils.iface.actionZoomToSelected().trigger()&#xa;">
      <actionScope id="Feature"/>
    </actionsetting>
  </attributeactions>
  <attributetableconfig sortOrder="0" sortExpression="" actionWidgetStyle="buttonList">
    <columns>
      <column width="57" type="actions" hidden="0"/>
      <column width="38" type="field" hidden="1" name="pk"/>
      <column width="82" type="field" hidden="0" name="warnlevel"/>
      <column width="93" type="field" hidden="0" name="warntext"/>
      <column width="165" type="field" hidden="0" name="layername"/>
      <column width="99" type="field" hidden="0" name="objname"/>
      <column width="168" type="field" hidden="0" name="warntyp"/>
      <column width="-1" type="field" hidden="0" name="attrname"/>
      <column width="159" type="field" hidden="0" name="createdat"/>
    </columns>
  </attributetableconfig>
  <conditionalstyles>
    <rowstyles/>
    <fieldstyles/>
  </conditionalstyles>
  <storedexpressions/>
  <editforminit/>
  <editforminitcodesource>0</editforminitcodesource>
  <editforminitfilepath></editforminitfilepath>
  <editforminitcode><![CDATA[# -*- coding: utf-8 -*-
"""
QGIS forms can have a Python function that is called when the form is
opened.

Use this function to add extra logic to your forms.

Enter the name of the function in the "Python Init function"
field.
An example follows:
"""
from qgis.PyQt.QtWidgets import QWidget

def my_form_open(dialog, layer, feature):
	geom = feature.geometry()
	control = dialog.findChild(QWidget, "MyLineEdit")
]]></editforminitcode>
  <featformsuppress>0</featformsuppress>
  <editorlayout>uifilelayout</editorlayout>
  <editable>
    <field editable="1" name="attrname"/>
    <field editable="1" name="beschreibung"/>
    <field editable="1" name="createdat"/>
    <field editable="1" name="gruppe"/>
    <field editable="1" name="idname"/>
    <field editable="1" name="layername"/>
    <field editable="1" name="name"/>
    <field editable="1" name="objname"/>
    <field editable="1" name="pk"/>
    <field editable="1" name="warnlevel"/>
    <field editable="1" name="warntext"/>
    <field editable="1" name="warntyp"/>
  </editable>
  <labelOnTop>
    <field name="attrname" labelOnTop="0"/>
    <field name="beschreibung" labelOnTop="0"/>
    <field name="createdat" labelOnTop="0"/>
    <field name="gruppe" labelOnTop="0"/>
    <field name="idname" labelOnTop="0"/>
    <field name="layername" labelOnTop="0"/>
    <field name="name" labelOnTop="0"/>
    <field name="objname" labelOnTop="0"/>
    <field name="pk" labelOnTop="0"/>
    <field name="warnlevel" labelOnTop="0"/>
    <field name="warntext" labelOnTop="0"/>
    <field name="warntyp" labelOnTop="0"/>
  </labelOnTop>
  <reuseLastValue>
    <field reuseLastValue="0" name="attrname"/>
    <field reuseLastValue="0" name="createdat"/>
    <field reuseLastValue="0" name="layername"/>
    <field reuseLastValue="0" name="objname"/>
    <field reuseLastValue="0" name="pk"/>
    <field reuseLastValue="0" name="warnlevel"/>
    <field reuseLastValue="0" name="warntext"/>
    <field reuseLastValue="0" name="warntyp"/>
  </reuseLastValue>
  <dataDefinedFieldProperties/>
  <widgets/>
  <previewExpression>"name"</previewExpression>
  <mapTip></mapTip>
  <layerGeometryType>4</layerGeometryType>
</qgis>
